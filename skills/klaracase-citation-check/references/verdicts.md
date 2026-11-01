# The seven verdicts

The verdict is always one of these seven words. Never invent an eighth. Only `discrepancy` says that something is wrong. The other six run from confirmation to absence of evidence.

| Verdict | What to tell the user |
| --- | --- |
| `verified_corpus` | The citation matches a real decision or a statute § in the corpus. This is not a claim that the law is correct, still good law, or supports the point it is cited for. It proves the decision exists, not that the quote or proposition holds. Read it with `get_decision` before relying on it. |
| `verified_external` | Confirmed by the external register. The MCP tool skips that stage, but this verdict can appear on a reused earlier run. |
| `not_found` | Not in the corpus. This never means the citation is invented. The corpus can lag inside its coverage windows, and this tool does not consult the external register, so the evidence is weaker than in the web app. |
| `out_of_coverage` | The citation lies outside the indexed range of that court, or outside the jurisdictions covered. Say both halves: it is outside the range, and its existence is not confirmed. Quote `coverage_boundary.from` and the German `coverage_advisory`. |
| `ambiguous` | Several corpus decisions match. The candidates are in `evidence`. Name them and ask which one the draft means. Relay the German `ambiguity_advisory`. |
| `unverifiable` | A tooling limit, not a statement about the citation. Examples: a superseded instrument such as the BBauG, a cost-schedule number, or an Absatz that could not be checked. Relay the advisory. |
| `discrepancy` | Found, and it contradicts the citation: wrong court or date, Urteil cited for a Beschluss, an Absatz that does not exist, a repealed §. The typed reason is in `evidence`. State the contradiction as the evidence gives it. |

## Rules

- Only `discrepancy` says something is wrong.
- `not_found` is absence of evidence, never proof that a citation is invented.
- `verified_corpus` proves the decision exists, not that the quote or proposition holds. Read it with `get_decision` before relying on it.
- The REST call (`POST /api/v1/citation-checks`) is corpus-only, like the MCP tool. It never consults the external register, so a `not_found` there is weaker evidence than in the web app.

## The `not_found` reasons

`evidence.reason` can specify a `not_found`:

- `statute_unknown`: the abbreviation matches no law Klaracase indexes. Say "we could not find this law", not "it does not exist".
- `state_law_out_of_scope`: a real Land-law citation. Klaracase cannot check Landesrecht, so say nothing about correctness.
- `section_absent_in_current_text`: the § is not in the current text of a law Klaracase holds. If decisions in the corpus cite that §, the verdict becomes `discrepancy` and `evidence.section_absence_advisory` explains that it may have been struck, renumbered or recodified.

## Fields to read with each verdict

| Verdict | Read these fields |
| --- | --- |
| `verified_corpus` | `matched_decision` (court, date, Aktenzeichen, `artifact_id`), `subdivision_check`, `subdivision_advisory`, `check_scope` |
| `verified_external` | `external_status`, `matched_decision` |
| `not_found` | `evidence.reason`, `evidence.advisory`, `evidence.section_absence_advisory` |
| `out_of_coverage` | `coverage`, `coverage_boundary.from`, `coverage_advisory` |
| `ambiguous` | `evidence` (the candidates), `ambiguity_advisory` |
| `unverifiable` | `evidence.reason`, `evidence.advisory` |
| `discrepancy` | `evidence` (the typed reason) |

`matched_decision.artifact_id` is the id that `get_decision` and `get_citation_graph` take.

## Run-level fields

- `partial`, `unverified_count`: citations left unchecked.
- `verdict_counts`, `unique_citations`: distinct citations. `findings`, `progress.citations_total`: occurrences.
- `extraction`: what was dropped instead of checked.
- `payload_truncated`, `truncation`: the answer was shortened to fit the size budget. Not the same as `partial`.
- `credits.cost`: what the call took.
