# After a timeout, don't do the same thing twice

> A reproducible VibeView 1.5.2 reading example. The “Paperboat Archive Service,” its endpoint, request parameters, idempotency keys, task IDs, and interactions are entirely fictional. They are used only to teach engineering mechanisms and do not represent a real product, incident, or measured result. No quantitative benefit is claimed.

## Original question

Our client calls an API to create an archive task, but the request times out. The server may have completed the work while its response was lost, or it may still be processing. If the client retries with a new idempotency key, could that create a duplicate task? How should the client and server handle retries safely? Explain the relationship among the key, request parameters, server-side records, concurrency, and expiration. Clearly state what is and is not guaranteed. Do not assume a specific API's undocumented behavior.

## Answer and technical context

A timeout tells the client that it does not know the result; it does not prove that the server did not execute the request. The request may not have arrived, may still be processing, or may have succeeded while the response was lost or delayed. Treat the result as **unknown**, not as a confirmed failure.

For a retry of the same business operation, reuse the original idempotency key and the same parameters within the API's documented retry and retention window. A new key represents a new operation and may create another task. Do not change the key just because the client timed out. Idempotency keys are not universal API behavior: the client must check the interface contract for support, scope, parameter comparison, retention, in-progress behavior, failure handling, and recovery after expiration.

Before execution, the server must perform authentication, authorization, and parameter validation. A record commonly includes a scope, key, normalized summary of relevant parameters, processing status, and completed business result or stable result reference. The server must reject the same key with different parameters and clearly report the conflict; it must not overwrite the record, silently reuse a mismatched result, or execute the request again. The API contract defines parameter normalization and comparison.

The processing rules are:

| Record state | Parameters | Server behavior |
| --- | --- | --- |
| No valid record exists | Request is valid | Atomically claim the key, then execute. A single ordinary lookup is not enough to safely start work. |
| Valid record is in progress | Match | Return an identifiable in-progress state or wait as specified; do not execute again. |
| Valid record is complete | Match | Return the saved business result or a stable reference. |
| Valid record exists | Differ | Reject the parameter conflict; do not execute a new operation. |
| Record expired or was deleted | Cannot be confirmed from the record | The original idempotency guarantee no longer holds. Check business state before choosing a recovery path. |

Idempotency is not created automatically by adding a field to a client request. It depends on durable server records, concurrency control, atomicity, and a retention period. Concurrent requests must not each execute after independently observing “no record”; a unique constraint, transaction, or equivalent atomic claim must ensure that only one worker owns a given valid key. The business commit and result record must also stay consistent, or a crash can leave the business operation successful while its record is missing. In this example, task creation and its completion record could share one transaction. For side effects across systems, a local transaction cannot cover remote actions; downstream idempotency, transactional messaging, reconciliation, or equivalent mechanisms are needed. A lock or cache alone does not solve these problems.

The record must have an explicit retention period coordinated with the client's retry window. After a record expires, is lost, or is deleted, the same key may be treated as a new request. Do not describe the key as providing “permanent deduplication” or unconditional exactly-once behavior across systems. For a timed-out operation past the retention window, query by a business identifier or follow the documented reconciliation and recovery procedure instead of blindly changing keys or continuing retries. The API contract must also define how failures, rollbacks, and retryable errors are recorded and when re-execution is allowed; not every failure means “nothing happened.”

The client's safest sequence is: save the key and its parameters before the first submission; treat a timeout as an unknown result; within the documented retry window, reuse that key and those parameters for the same business operation, querying or retrying with backoff as the API specifies; generate a new key only for an explicitly new business intent. The server must reject parameter conflicts, claim keys atomically, keep business commits and records consistent, and define retention and recovery rules.

In short: retries repeat the transmission, not the business intent. A timeout does not mean the operation did not run. Reuse the key for the same operation and use a new key for a new one; the guarantee depends on server records, atomicity, and retention.

## Page authoring brief

Turn the answer above into a readable webpage rather than copying it paragraph by paragraph. Use an editorial, light-violet layout. Explain “the operation succeeded but the client timed out” with a request-and-receipt sequence diagram. Compare retrying with the same key against creating a new operation with a new key. Preserve the complete processing rules and the limits of the guarantee. Use a text-only `VibeView.` brand, English body copy, a desktop reference width of 1280px, and a simple narrow-screen layout. Use no JavaScript, external fonts, or images. Do not invent quantitative benefits. Explicitly identify the entire business scenario as fictional.

## Reproducible build

This Markdown file is the semantic source; `reading-map.fragment.html` is the visual body authored from it. `compose.py` assembles HTML fragments and does not parse Markdown. The final page is built with the release's 1.5.2 `SKILL.md`, scripts, and embedded styles from the same directory.

Run the following from the `vibeview` directory. The `docs` directory must exist and `docs/index.html` must not; the composer never overwrites an existing output. `-B` prevents Python bytecode cache files.

```bash
python3 -B scripts/compose.py examples/reading-map.fragment.html docs/index.html --title 'After a timeout, don’t do the same thing twice' --theme violet
```

The composer prefixes the HTML title with `VibeView ·`; the body heading is “After a timeout, don’t do the same thing twice.” Building does not launch a browser or publish a webpage.
