---
name: klaracase-german-legal-research
description: Use when the user asks what German courts decided on a legal question, wants Rechtsprechung, decisions with Aktenzeichen, the text of a decision or of a statute (for example "§ 535 BGB"), the case law on a §, or which decisions cite a decision. Searches and reads German case law and statutes with Klaracase, through its MCP tools (search_decisions, get_decision, get_norm, get_citation_graph and more) or its REST API. Covers which tool fits which question, how to phrase German queries, how to read results and how to cite them. German law only.
license: MIT
metadata:
  author: "SPARQ VENTURES UG (haftungsbeschränkt)"
  homepage: "https://klaracase.de"
  version: "1.0.0"
---

# German legal research with Klaracase

Klaracase holds German court decisions and German statutes, linked by a resolved citation graph. It covers German law only.

Klaracase is a research tool. It finds and verifies sources. It gives no legal advice and does not replace a lawyer's review. Say so when the user asks for a recommendation on their own case, and keep to what the sources say.

## When not to use it

- The question concerns another legal system than German law. Do not use Klaracase.
- The question is not legal. Do not use Klaracase.
- The user wants the citations in a text checked. Use the skill `klaracase-citation-check`.

## Connect

```
MCP server (streamable HTTP):  https://klaracase.de/mcp
Auth:        Bearer token, or OAuth sign-in in clients that support it
Token page:  https://klaracase.de/settings/api-tokens
REST base:   https://klaracase.de/api/v1   (Authorization: Bearer <token>)
```

The same token works as a Bearer token on MCP and on REST. If the host has the Klaracase MCP tools, use them. If it has only a token and a shell or an HTTP client, use REST: see `references/rest.md`. If it has neither, tell the user to connect the MCP server or create a token.

Five token abilities exist: `search`, `read`, `graph`, `datapackage`, `citation-check`. A missing one is refused with `token_ability_missing` before anything runs. New verified accounts get 30 free credits, valid for 30 days. Tool guide: https://klaracase.de/docs/mcp/tools-guide

## Choose the tool

| The user wants | Use | Credits |
| --- | --- | --- |
| Decisions on a legal question | `search_decisions` | 1 per distinct query |
| The statute and the case law together | `cross_type_search` | 1 per distinct query |
| One decision, by Aktenzeichen, ECLI or `id` | `get_decision` | 1 per decision per calendar month |
| One statute norm, by citation ("§ 535 BGB", "Art. 6 DSGVO") | `get_norm` | 1 per norm per calendar month |
| What a decision relies on, or who cites it | `get_citation_graph` | 2 per call |
| Several known decisions as one grounded package | `assemble_datapackage` | 5 per call |
| Whether the collection holds a court or period | `corpus_coverage` | free |
| Valid values for a filter | `list_facets` | free |

Arguments, caps, abilities and the REST twin of each tool are in `references/tools.md`. A repeat of the same call in the same billing period reports `cost: 0`. Read `credits.cost` in the answer for what a call took. Prefer the free tools first when a filter or a coverage question is open.

## Work in this order

1. **Find.** Use `search_decisions` for case law, or `cross_type_search` when the statute matters as much as the case law. A row's `id` is the handle for `get_decision`, `get_citation_graph` and `assemble_datapackage`.
2. **Read.** Use `get_decision` for the text of the one or two decisions that matter. Use `get_norm` for the wording of a statute. Do not summarize a decision from the search row alone when the user needs its reasoning.
3. **Follow.** Use `get_citation_graph` to see which decisions a decision cites (`references`) and which later decisions cite it (`referenced_by`), for example to judge whether a line of case law is settled.
4. **Bundle.** Use `assemble_datapackage` only when the user has already picked several decisions and wants them as one structured package for a memo or comparison. Put the most important ids first, because the response budget drops decisions from the end.

## Write good queries

- Use German legal concepts, not bare keywords. Example: "Widerrufsrecht Fernabsatzvertrag Wertersatz Verbraucher". If the user writes in English, translate the concept into German terms before you search.
- A query over 500 characters is rejected, not truncated. Do not paste a whole document into `query`.
- A query that is a citation throughout ("§ 550a BGB", "VIII ZR 311/02") is matched exactly. A similar number will not answer it.
- Narrow with filters instead of making the query longer: `court`, `branch`, `document_type`, `cited_norm` (one canonical §-token such as "§ 906 BGB"), `cited_statutes` (for example `["StGB", "StPO"]`), `date_from` and `date_to` (YYYY-MM-DD).
- `branch` is the Gerichtsbarkeit (court jurisdiction) that decided the case, never the legal subject area. `patent` is the Bundespatentgericht alone. BGH patent decisions sit under `ordentlich`.
- Take filter values from `list_facets` (fields `court_name`, `court_branch`, `document_type`, `jurisdiction`, `law_type`, `cited_norms`) instead of guessing. `cited_norms` needs a `norm`, for example `{"field": "cited_norms", "norm": "§ 249 BGB"}`. A value that `list_facets` does not list can still filter.
- `search_decisions` returns at most 20 rows per page and `page` runs from 1 to 10. `page` and `limit` are free. `cross_type_search` returns 5 rows per section by default, at most 10.
- In `cross_type_search`, `jurisdiction` narrows the laws section only. The court filters narrow the decisions section only. Check `filters_applied_sections` to see which section a filter ran on. A section it does not name was searched without that filter.
- For a known Aktenzeichen, call `get_decision` and do not search. Write the Aktenzeichen in its normal spacing and casing ("VIII ZR 271/17"). If several courts share it, the tool refuses with a candidate list, so add `court` or `date`.

## Read the fields that qualify the rows

Do not report the rows alone. Read these fields and say what they mean in your answer.

- `total_available` is a floor band `{value, is_floor}`, not an exact count and not an upper bound on the rows served. Do not quote it as "there are exactly N decisions".
- `candidate_pool`, `pool_exhaustive` and `truncated` say whether anything that matches remains beyond what was served. `payload_truncated` says the answer was shortened to fit the size budget.
- `filters_applied` records what the search ran with. Check that it matches what the user asked.
- `confidence` (`high`, `medium`, `low`) bands a row's relevance. `null` means not measured, never low. It does not reorder anything.
- A scanned decision can carry a wrong stored date. Read `date_source` and `date_confidence` before you rely on a date filter or quote a date.
- `rn_source` says whether a Randnummer may be cited. Cite a Randnummer only when it allows that.
- On `get_decision`, `truncated` means your `max_chars` cut the text. `metadata.file_numbers` is the full set of file numbers of a joined proceeding, and `joined_proceeding_note` explains it. The `title` can hide a docket behind "u. a.".
- On `get_norm`, read `norm.lifecycle` (current, repealed, unconfirmed), `law.upstream_status` and `version.last_amendment_date` to say whether the text is current and as of when. An Absatz in the reference is echoed with whether it exists, and the text is always the whole norm. Only the current text is served. A request for an older version (a.F.) is refused.
- On `get_citation_graph`, every edge has a `resolution_status`. Edges are extracted from decision texts, so a missing edge is not proof that a decision cites nothing. An unresolved edge is a real extracted citation whose target is not identified, so never present it as corpus-verified.

## Empty or thin results

An empty result does not prove that no such case law exists.

1. Call `corpus_coverage` (free) for the court or `branch` and read the earliest and latest decision dates. A zero can mean that the period or court is not covered. A court's `earliest` is not where ingestion starts. Read `coverage_ranges` for the boundary.
2. Call `list_facets` to check that the filter value exists in the index.
3. Rephrase the query in other German legal terms, or remove one filter.
4. `search_timeout` and `index_unavailable` are failures, not an empty collection. Retry later and tell the user the search did not run.

## Cite only what a tool returned

- Name every Aktenzeichen and norm in your answer from a tool result. Every Aktenzeichen the tools return exists in the corpus. A file number no tool returned has no source in Klaracase, so do not add one from memory.
- Give court, decision date and Aktenzeichen for each decision, as the tool served them, and say which tool call the statement rests on.
- State what you did not read. If you only saw a search row, say you did not read the decision text.
- Do not turn a reported decision into legal advice. Describe what the sources hold and where they disagree.

## When a call is refused

A refusal carries an `error_code` (REST: `code`) and a `message` (REST: `detail`) that says what the user has to do, for example sign in again, create an organization or set up two-factor sign-in. Pass that message on. `insufficient_credits` means the balance cannot pay for the call, and credits are bought on klaracase.de. `volume_cap` means a daily limit was reached, and nothing ran or was charged. Wait the stated `retry_after_seconds`. The rate limit is 60 requests per minute per token. Do not retry in a loop.
