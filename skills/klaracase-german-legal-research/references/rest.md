# Legal research over REST

Use this when the host has an API token but no MCP client. Each REST operation is the twin of an MCP tool, with the same arguments, the same answer and the same price.

- Base URL: `https://klaracase.de/api/v1`
- Auth: `Authorization: Bearer <token>`. The same token works on MCP at `https://klaracase.de/mcp`.
- Token page: https://klaracase.de/settings/api-tokens. Tick the abilities you need.
- Keep the token in the environment variable `KLARACASE_API_TOKEN`. Never write it into a file, a prompt or a log.
- API reference: https://klaracase.de/docs/api. The OpenAPI file is public: https://klaracase.de/api/v1/openapi.json

## The twins

| MCP tool | REST call | Credits | Ability |
| --- | --- | --- | --- |
| `search_decisions` | `GET /decisions/search?query=...` | 1 | `search` |
| `cross_type_search` | `GET /search?query=...` | 1 | `search` |
| `get_decision` | `GET /decisions/{id}` | 1 | `read` |
| `get_norm` | `GET /norms/{reference}` | 1 | `read` |
| `get_citation_graph` | `GET /decisions/{id}/citations` | 2 | `graph` |
| `assemble_datapackage` | `POST /datapackages` (JSON body) | 5 | `datapackage` |
| `check_citations` | `POST /citation-checks` (JSON body) | from 2 | `citation-check` |
| `corpus_coverage` | `GET /corpus/coverage` | free | `read` |
| `list_facets` | `GET /corpus/facets/{field}` | free | `read` |

The query and body parameters have the same names as the MCP arguments. Two differences: on REST, `corpus_coverage` and `list_facets` need the ability `read` (on MCP they need `search`), and `GET /decisions/{id}/citations` is the REST name of `get_citation_graph`.

## Examples

```bash
# Search (1 credit)
curl -sS -G https://klaracase.de/api/v1/decisions/search \
  -H "Authorization: Bearer $KLARACASE_API_TOKEN" \
  --data-urlencode "query=Widerrufsrecht Fernabsatzvertrag Wertersatz Verbraucher" \
  --data-urlencode "court=BGH" \
  --data-urlencode "date_from=2015-01-01"

# Read one decision by Aktenzeichen. Encode the slash as %2F (1 credit)
curl -sS "https://klaracase.de/api/v1/decisions/VIII%20ZR%20271%2F17?section=Gr%C3%BCnde" \
  -H "Authorization: Bearer $KLARACASE_API_TOKEN"

# Read one norm (1 credit)
curl -sS "https://klaracase.de/api/v1/norms/%C2%A7%20535%20BGB" \
  -H "Authorization: Bearer $KLARACASE_API_TOKEN"
```

Rules for the HTTP call:

- Encode path parameters as one segment: a slash in an Aktenzeichen becomes `%2F`, and a norm such as `§ 535 BGB` is percent-encoded.
- Send array filters in the form `cited_statutes[]=StGB&cited_statutes[]=StPO`.
- Send booleans (`bridge`) as `true` or `false`. Leave out parameters you do not use.
- Do not build query strings by hand. Use `curl -G --data-urlencode` or an HTTP library.

## Errors

Every error is `application/problem+json` with `type`, `title`, `status`, `detail` and `code`. The `code` vocabulary is the one the MCP tools serve as `error_code`. Branch on `code`. Do not fetch the `type` URL as a page.

| `code` | Status | Extra members | What to do |
| --- | --- | --- | --- |
| `unauthenticated` | 401 | | The token is missing, expired or revoked. |
| `token_ability_missing` | 403 | `required_ability` | The user creates a token with that ability ticked. |
| `insufficient_credits` | 402 | `cost`, `balance` | Tell the user to buy credits on klaracase.de. Do not retry. |
| `rate_limited` | 429 | `retry_after_seconds` | Wait that long, then retry. Nothing ran. The limit is 60 requests per minute per token. |
| `volume_cap` | 429 | `unit`, `cap`, `resets_at`, `retry_after_seconds` | A daily cap was reached. Nothing ran or was charged. |
| `validation_failed` | 422 | `errors` | Fix the named argument. |
| `not_found` | 404 | | No such decision or norm. Try `get_decision` with the exact Aktenzeichen, or search. |
| `ambiguous_aktenzeichen` | 422 | `candidates` | Add `court` or `date`. |
| `search_timeout`, `index_unavailable`, `backend_unavailable` | 503 | | The call did not run. Retry later. Do not report it as an empty result. |

A 429 or 503 means nothing ran and nothing was charged, so a retry is safe. Never retry a 402 or another 4xx.

Every answer carries the header `X-Klaracase-Api-Release`. Answers carry `credits: {metered, cost, credits_remaining}` and, when you sent an unknown argument, `ignored_parameters`.

## Official SDKs

Official SDKs: see the Klaracase GitHub organization.
