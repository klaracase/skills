# Klaracase MCP tools

MCP server: `https://klaracase.de/mcp`. Full guide: https://klaracase.de/docs/mcp/tools-guide

Prices are in credits. One charge applies per operation, organization, subject and calendar month (UTC). A repeat in the same month reports `cost: 0`, on MCP or REST. Read `credits.cost` in the answer for what a call took.

| Tool | Arguments (required in bold) | Caps and defaults | Credits | Token ability |
| --- | --- | --- | --- | --- |
| `search_decisions` | **`query`**, `court`, `branch`, `document_type`, `cited_norm`, `cited_statutes`, `date_from`, `date_to`, `mode`, `limit`, `page`, `bridge` | `query` 2 to 500 characters (longer is rejected). `limit` default 20 and hard cap 20. `page` 1 to 10. `cited_statutes` up to 5. `mode` `keyword`, `semantic` or `hybrid` (default). `bridge` default true. | 1 per distinct query and filter set; paging is free | `search` |
| `cross_type_search` | **`query`**, `jurisdiction`, `court`, `branch`, `document_type`, `cited_norm`, `cited_statutes`, `date_from`, `date_to`, `mode`, `limit`, `bridge` | Same `query` rule. `limit` is per section, default 5, hard cap 10. No `page`. `jurisdiction` (`DE`, `EU`, `XI`) filters the laws section only. The court filters apply to the decisions section only. | 1 per distinct query | `search` |
| `get_decision` | **`id`** (UUID, Aktenzeichen or ECLI), `max_chars`, `rn_from`, `rn_to`, `section`, `court`, `date` | `max_chars` default 40,000, minimum 500. `section` is one of Tenor, Leitsatz, Tatbestand, Gründe (case-insensitive). `court` and `date` disambiguate an Aktenzeichen. | 1 per decision per month; any slice of it again is free | `read` |
| `get_norm` | **`reference`** (one citation such as "§ 535 BGB" or "Art. 6 DSGVO"), `jurisdiction` | One norm per call, up to 120 characters. Current consolidated text only. A range is refused with `range_not_supported`. "a.F." is refused with `historical_version_unavailable`. `jurisdiction` is `DE` or `EU`. | 1 per norm per month | `read` |
| `get_citation_graph` | **`id`**, `direction`, `depth`, `court`, `date`, `page` | `direction` is `outgoing`, `incoming` or `both` (default). `depth` is 1 (default) or 2. Depth 2 serves at most 50 neighbours. `page` 1 to 20 with 25 neighbours per page and direction, depth 1 only. | 2 per call | `graph` |
| `assemble_datapackage` | **`ids`**, `include_citations`, `full_text`, `max_chars` | `ids` 1 to 10 (UUID or Aktenzeichen), most important first. `include_citations` default true. `full_text` default false. `max_chars` 500 to 200,000, default 60,000, a ceiling and not a guarantee. | 5 per call | `datapackage` |
| `check_citations` | **`text`**, `reference_date` | `text` 50 to 20,000 characters. See the skill `klaracase-citation-check`. | `max(2, ceil(characters / 5000))`: 2 up to 10,000, 3 up to 15,000, 4 at 20,000 | `citation-check` |
| `corpus_coverage` | `branch`, `top` | `top` default 20, maximum 100. The branch rollup is never capped. | free | `search` |
| `list_facets` | **`field`**, `type`, `norm`, `prefix` | `field` is `court_name`, `court_branch`, `document_type`, `jurisdiction`, `law_type` or `cited_norms`. `norm` is required with `cited_norms`. `type` is `decision` or `law`. | free | `search` |

## Filter values

- `branch`: `ordentlich`, `verwaltung`, `sozial`, `arbeit`, `finanz`, `verfassung`, `patent`, `unbekannt`. A branch is a court jurisdiction, never a subject area.
- `document_type`: `Urteil`, `Beschluss`, `Verfügung`, `Sonstige`, `Gerichtsbescheid`, `Schlussanträge`.
- `cited_statutes`: `StGB`, `StPO`, `InsO`, `DSGVO`, `GDPR`, `BDSG`, `BauGB`, `BBauG`, `BauNVO`, `StVG`, `StVO`.
- Dates are `YYYY-MM-DD`. An inverted range is refused.

## Limits

- Rate limit: 60 requests per minute per token. Above that, the server returns JSON-RPC error -32000 (HTTP 429) with `data.retry_after_seconds`. Nothing ran.
- Daily volume caps (rows or documents, Europe/Berlin day): free 1,000 and 40, Starter 5,000 and 200, Professional 20,000 and 600, Enterprise 60,000 and 2,000. A reached cap is refused with `volume_cap`.
- Free accounts get 30 credits once, valid for 30 days. Starter has 300 credits a month, Professional 1,000, Enterprise 5,000. Credits do not roll over. Plan prices are on https://klaracase.de/preise (German) and https://klaracase.de/en/preise (English).

## Area addresses

Preset filters per legal area are available at `https://klaracase.de/mcp/{key}`. Keys: `steuerrecht`, `arbeitsrecht`, `sozialrecht`, `verwaltungsrecht`, `verfassungsrecht`, `patent-markenrecht`, `strafrecht`, `insolvenzrecht`, `datenschutzrecht`, `baurecht`, `verkehrsrecht`.

## Clients that speak only stdio

Use the bridge `npx mcp-remote https://klaracase.de/mcp`.
