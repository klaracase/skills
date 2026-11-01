# Citation check over REST

Use this when the host has an API token but no MCP client. The REST call is the twin of the MCP tool `check_citations`: same arguments, same answer, same price.

## Setup

- Token page: https://klaracase.de/settings/api-tokens (needs a login and a verified email). Tick the ability `citation-check`. The token is bound to the organization that is open when you create it, and every call is billed there.
- Base URL: `https://klaracase.de/api/v1`
- Auth header: `Authorization: Bearer <token>`. The same token works on MCP at `https://klaracase.de/mcp`.
- Keep the token in the environment variable `KLARACASE_API_TOKEN`. Never write it into a file, a prompt or a log.
- API reference: https://klaracase.de/docs/api. The OpenAPI file is public: https://klaracase.de/api/v1/openapi.json

## Run a check

```bash
curl -sS https://klaracase.de/api/v1/citation-checks \
  -H "Authorization: Bearer $KLARACASE_API_TOKEN" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  --data "$(jq -n --rawfile text draft.txt --arg reference_date 2026-10-01 \
        '{text: $text, reference_date: $reference_date}')"
```

- `text`: 50 to 20,000 characters of German legal text, sent unchanged. Offsets in the answer are Unicode codepoint offsets into this exact string. Use `jq --rawfile` or a JSON library to encode it. Do not build the JSON by hand.
- `reference_date`: optional, `YYYY-MM-DD`. Drop it from the `jq` call when the user gave no date.
- Instead of `text` you can send `document_id`, the id of an upload whose `status` is `ready` (never both). Upload with `POST /citation-check-documents` (multipart field `file`; PDF, DOCX, Markdown or text; up to 25 MB; free). The answer is 202. Poll `GET /citation-check-documents/{document}` until `status` is `ready`. The receipt names `char_count`, `check_max_chars` and `quoted_credits`. An upload that is not used expires after 48 hours.
- The call is synchronous. The 200 answer is the finished run, with a terminal `status`. There is nothing to poll.
- It needs the ability `citation-check`. It costs from 2 credits (2 up to 10,000 characters, 3 up to 15,000, 4 at 20,000). The same text again in the same billing period costs 0, on REST or MCP.
- The call is corpus-only. It does not consult the external register.
- The check is saved in the user's Citation Check history. The input text is deleted after 90 days. The findings are kept.

## Read the run back

```bash
curl -sS "https://klaracase.de/api/v1/citation-checks/$RUN_ID" \
  -H "Authorization: Bearer $KLARACASE_API_TOKEN" \
  -H "Accept: application/json"
```

`RUN_ID` is the `id` of the 200 answer. The read-back is free. It reads only runs made through the API by your organization. The answer has the same shape as the POST answer. Read it with the same rules as the MCP answer: `references/verdicts.md`.

## Errors

Every error is `application/problem+json` with `type`, `title`, `status`, `detail` and `code`. Branch on `code`, not on `detail`. Do not fetch the `type` URL as a page.

| `code` | Status | What to do |
| --- | --- | --- |
| `text_too_long` | 422 | The text is over 20,000 characters. Nothing was charged. Send the user to the web app Citation Check, which takes up to 150,000 characters. |
| `not_german_legal_text` | 422 | The text shows fewer than two legal-signal categories. Nothing was charged. Send the surrounding sentences. Padding does not help. |
| `validation_failed` | 422 | A text under 50 characters, or a `reference_date` that is not a calendar day. The `errors` member names the argument. Fix it and retry. |
| `insufficient_credits` | 402 | The balance cannot pay. `cost` and `balance` are in the problem. Tell the user to buy credits on klaracase.de. Do not retry. |
| `rate_limited` | 429 | Wait `retry_after_seconds` (also the `Retry-After` header), then retry. Nothing ran and nothing was charged. This POST has its own limit of 10 requests per minute per token. |
| `token_ability_missing` | 403 | The token lacks the ability named in `required_ability` (`citation-check`). The user creates a new token with that ability ticked. |
| `unauthenticated` | 401 | The token is missing, expired or revoked. |
| `backend_unavailable` | 503 | The check did not run and the charge was given back. Tell the user. Do not report it as a result. |

Other codes that can occur: `token_org_missing`, `token_org_membership_lost`, `two_factor_required`, `volume_cap`, `document_unavailable`. Pass on the `detail` to the user.

A 429 or 503 means nothing ran and nothing was charged, so a retry is safe. Never retry a 402 or another 4xx.

Every answer carries the header `X-Klaracase-Api-Release`.

## Official SDKs

Official SDKs: see the Klaracase GitHub organization.
