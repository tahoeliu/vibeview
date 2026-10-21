# Retry the request. Reuse the result.

A reproducible VibeView example about API retries and idempotency. The service, endpoint, parameters, keys, and task IDs are fictional.

## The question

Our client asks an API to create an archive task, but the request times out. The server might have completed the work, or it might still be processing. Could retrying with a new idempotency key create a second task? Explain how the client and server can handle retries safely, including concurrency, parameter conflicts, and expired records. State the assumptions and limits without inventing an API contract.

## The explanation

A timeout leaves the client with an unknown result. The request may never have reached the server, may still be running, or may have succeeded before its response was lost. A timeout alone cannot tell the client which case occurred.

If the API supports idempotency keys, the client should save the key and request parameters before the first attempt. To retry the same operation, reuse that key and those parameters within the API’s documented retry window. A new key can represent a new operation and create another task, even if its parameters match the first request.

The API contract must define the key’s scope, how it compares parameters, how long it keeps records, how it reports work in progress, which failures permit another attempt, and how clients recover after a record expires. An idempotency key is not an authentication credential: the server must authenticate the caller, check authorization, and validate the request before using it.

### What the server records

A typical record links the key to its scope, the relevant normalized request parameters, the processing state, and the result or a stable reference to it. In this example, key `K-A` in the archive endpoint’s scope maps to task `ARC-17` for `project=demo, format=zip`.

The key must be sufficiently unique within its scope. The API must define parameter normalization and comparison. If the same key arrives with different parameters, reject the conflict rather than overwriting the record, returning an unrelated result, or starting another operation.

| Stored state | Parameters | Expected behavior |
| --- | --- | --- |
| No valid record | Valid request | Atomically claim the key, then execute the operation. |
| In progress | Match | Report work in progress or wait as specified by the API. Do not execute again. |
| Complete | Match | Return the saved result or a stable reference to it. |
| Valid record exists | Differ | Reject the parameter conflict. |
| Expired or deleted | Cannot be verified | Check business state and follow the documented recovery procedure. The original guarantee may no longer apply. |

### Three conditions that make the guarantee work

**Concurrent requests must claim the key atomically.** Two workers can both look up a key and find nothing. A unique constraint, transaction, or equivalent atomic mechanism must decide which worker owns the operation. A lookup followed by an unprotected write is insufficient.

**The operation and its record must stay consistent.** A crash must not leave completed work with no deduplication record. In this example, task creation and its record can commit in one transaction. Remote side effects may need downstream idempotency, transactional messaging, or reconciliation. A local lock, transaction, or cache does not automatically protect work in another system.

**The retry window must fit within record retention.** An expired, deleted, or lost record may cause the same key to be treated as new. After expiration, query by a business identifier or reconcile the result before following the recovery procedure. Do not assume permanent deduplication or unconditional exactly-once execution across systems.

The API must also specify how it records failures and rollbacks, and when re-execution is permitted. A failed response does not always mean the operation never ran. Backoff reduces traffic; it does not deduplicate work. Reusing the operation’s result does not require every response header or byte to be identical.

### The practical rule

Save the key and parameters before sending. Treat a timeout as an unknown result. For the same operation, query or retry with the original key and parameters as the API specifies. Generate a new key only when intentionally starting a new operation. Once the retention window has passed, establish what happened before attempting recovery.

## What the visual guide should show

Lead with one case: the server creates `ARC-17`, but the client never receives the response. A retry with `K-A` and matching parameters returns that task’s saved result while the record is valid. Then compare a retry with a genuinely new operation, show the full decision table, and explain concurrency, consistency, and retention. Keep these conditions visible alongside the diagram.
