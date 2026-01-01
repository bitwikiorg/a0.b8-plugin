# 📜 B8 Link Protocol Specification (v1.0.0)

## 1. Message Envelope
All synaptic transmissions must adhere to the following JSON structure:
```json
{
  "type": "string",           // 'chat', 'post', 'core_trigger'
  "channel": "string",        // Category ID or Topic ID
  "content": "string",        // Raw markdown or JSON string
  "metadata": {               // Optional context
    "correlation_id": "uuid", // For end-to-end tracing
    "idempotency_key": "uuid" // To prevent duplicate processing
  },
  "ts": "iso8601",            // Timestamp of emission
  "ttl": "integer"            // Time-to-live in seconds
}
```

## 2. Transport & Auth
- **Endpoint**: Defined by `BITHUB_URL`.
- **Authentication**: Header `User-Api-Key` required for all requests.
- **Content-Type**: `application/json`.

## 3. Error Taxonomy
| Code | Type | Client Behavior |
|---|---|---|
| 401/403 | Auth Failure | Halt; check API Key. |
| 429 | Rate Limit | Wait for `Retry-After` header; exponential backoff. |
| 5xx | Server Error | Retry up to 3 times with backoff. |
| 422 | Validation | Do not retry; check payload schema. |

## 4. Idempotency & Retries
- POST requests to `/posts.json` should include an `idempotency_key` in metadata to prevent duplicate posts during network jitter.
- Safe to retry: GET, DELETE, PUT.
