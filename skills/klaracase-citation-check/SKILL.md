---
name: klaracase-citation-check
description: Use when the user pastes a German legal text (Schriftsatz, Urteil, Beschluss, memo, draft, or an AI-written legal text) and asks to check its citations, "Fundstellen prüfen", "Zitate prüfen", or whether the decisions and statutes are real, correctly cited or traceable. Runs the Klaracase citation check through the MCP tool check_citations or the REST call POST /api/v1/citation-checks, and reports one of seven verdicts per citation. Also says when get_decision or get_norm is enough, how to read partial runs, and the length limits. German law only.
license: MIT
metadata:
  author: "SPARQ VENTURES UG (haftungsbeschränkt)"
  homepage: "https://klaracase.de"
  version: "1.0.0"
---

# Checking citations with Klaracase

Klaracase holds German court decisions and German statutes, linked by a resolved citation graph. Its citation check reads a German legal text, finds every court-decision and statute citation in it, and traces each one to a source in the Klaracase corpus. The result is traceability: it shows which citations can be found, not whether the law is right.

The citation check returns one verdict per citation, with offsets into the exact text you sent. It is a research tool. It gives no legal advice and does not replace a lawyer's review.

## When not to use it

- The text is about another legal system than German law. Klaracase covers German law only.
- The question is not legal.
- The user wants to know whether a decision supports a point. A citation check does not answer that. See "Pick the right tool".

## Connect

```
MCP server (streamable HTTP):  https://klaracase.de/mcp
Auth:        Bearer token, or OAuth sign-in in clients that support it
Token page:  https://klaracase.de/settings/api-tokens
             (ability needed for check_citations: citation-check)
REST base:   https://klaracase.de/api/v1   (Authorization: Bearer <token>)
```

The same token works as a Bearer token on MCP and on REST. If the host has the Klaracase MCP tools, use them. If it has only a token and a shell or an HTTP client, use REST: see `references/rest.md`. If it has neither, tell the user to connect the MCP server or create a token. Do not guess the answer.

New verified accounts get 30 free credits, valid for 30 days. Tool guide: https://klaracase.de/docs/mcp/tools-guide

## Pick the right tool

- **A text with several citations:** use `check_citations`. This is the case for a draft, a Schriftsatz, a memo, or text written by an AI model.
- **One decision the user already named:** use `get_decision` with the Aktenzeichen. It confirms the decision exists and lets you read what it says.
- **One statute citation:** use `get_norm` ("§ 626 Abs. 2 BGB"). It returns the current wording of that norm.
- **Does a decision say what the draft claims it says?** `check_citations` does not answer that. Read the decision with `get_decision`, using a Randnummer window or a named `section`, and compare.
- **Finding authority for a point in the draft:** use `search_decisions` or `cross_type_search`. `check_citations` does not find decisions. The skill `klaracase-german-legal-research` covers them.

## Before you call it

- `text` is required. It must be at least 50 characters and at most 20,000 characters. Longer input is refused with `text_too_long`.
- Long documents belong in the Citation Check of the Klaracase web app at klaracase.de, which takes documents of up to 150,000 characters, also consults the external register, and can re-check a run. Tell the user that, instead of cutting their document without saying so.
- The text must show at least two of five legal-signal categories: a norm with § or Artikel, a German court, an Aktenzeichen-shaped docket, German legal-prose markers ("Abs.", "Urteil", "vgl."), or English legal markers. A lone statute sentence is refused with `not_german_legal_text`, however long it is. Send the surrounding sentences or the cited decision. Padding does not help.
- `reference_date` is optional (`YYYY-MM-DD`). It dates statute citations whose own sentence names no date, and only affects the pre-reform-numbering advisory. It changes no verdict. Pass the document date when the user gives one.
- Send the user's text unchanged. Offsets in the answer are Unicode codepoint offsets into that exact string.
- The call is not read-only. Each check is saved in the user's Citation Check history in Klaracase, and the input text is deleted after 90 days (the findings are kept). It costs credits: at least 2, and more for longer text (2 up to 10,000 characters, 3 up to 15,000, 4 at 20,000). `credits.cost` is what the call took. Identical text again in the same billing period costs 0. If the user did not clearly ask for a check, say what it costs and that it is saved before you run it.

## The seven verdicts

The verdict is always one of these seven words. Never invent an eighth. Only `discrepancy` says that something is wrong. `not_found` is absence of evidence, never fabrication. The other five run from confirmation to a limit of the tool.

- `verified_corpus`: the citation matches a real decision or a statute § in the corpus. It proves the decision exists, not that the quote or proposition holds. Read it with `get_decision` before relying on it.
- `verified_external`: confirmed by the external register. The MCP tool and the REST call skip that stage, but this verdict can appear on a reused earlier run.
- `not_found`: not in the corpus. Absence of evidence, never fabrication.
- `out_of_coverage`: outside the indexed range of that court, or outside the jurisdictions covered.
- `ambiguous`: several corpus decisions match.
- `unverifiable`: a tooling limit, not a statement about the citation.
- `discrepancy`: found, and it contradicts the citation.

The exact wording to give the user for each verdict, the `evidence.reason` values of `not_found`, and the fields that go with each verdict are in `references/verdicts.md`. Read that file before you report a run.

## Read the fields that qualify the verdicts

- `partial` and `unverified_count` say the run left citations unchecked. Never present such a run as fully checked. Say how many citations are unverified. A re-check of that run in the web app costs nothing and covers exactly those citations. Calling the tool again re-checks the whole text. Identical text costs 0 in the same billing period. Changed text is priced again.
- `check_scope` and `subdivision_check` say how far down the citation the check looked. `verified_corpus` on "§ 573 Abs. 2 Nr. 2 BGB" can mean only the § and the Absatz were checked. Relay `subdivision_advisory` (for example "Abs. 1 bestätigt; Nr. 2 nicht geprüft") instead of saying "fully verified".
- `check_scope.court` says whether the court named in the prose was compared. `unchecked` means not checked. It changes no verdict.
- `verdict_counts` and `unique_citations` count distinct citations. `findings` and `progress.citations_total` count occurrences. Say "citations", not "mentions".
- `extraction` counters say what was dropped instead of checked. Name those passages to the user, because the check is incomplete there.
- `payload_truncated` says the answer was shortened to fit the size budget. `truncation` names what was shed. This differs from `partial`.
- The German advisory strings (`coverage_advisory`, `ambiguity_advisory`, `subdivision_advisory`, `ecli_advisory`, `evidence.advisory`, `evidence.section_absence_advisory`) are finished sentences. Show them as they stand.
- An advisory such as `rechtsmittel_entschieden` or `possible_pre_reform_numbering` is information, not a defect and not a verdict.

## Report the result

1. Start with the totals: how many distinct citations, how many per verdict, and whether the run was `partial`.
2. List each distinct citation once, in reading order, from `unique_citations`. Give the citation as the user wrote it, its verdict, and in one sentence what that verdict means here. Do not group on `raw_text`.
3. For `verified_corpus` on a decision, give court, date and Aktenzeichen from `matched_decision`. Do not state more than the verdict says.
4. For every `not_found`, `out_of_coverage`, `ambiguous`, `unverifiable` and `discrepancy`, give the reason and what the user can do next. For a missing decision, try `get_decision` with the exact Aktenzeichen or `search_decisions` for a near match. Say what each of those returned.
5. Never call a citation fabricated, invented or non-existent beyond what its verdict says. `not_found` is not such a claim. Only `discrepancy` says that something is wrong, and only in the way its evidence states.
6. Close with what the check did not cover: corpus only, no external register, Satz, Nr. and lit. below the § not checked, and whether the cited decisions support the propositions they are cited for.

## Cite only what a tool returned

- Name every Aktenzeichen and norm in your answer from a tool result. Every Aktenzeichen the tools return exists in the corpus. A file number no tool returned has no source in Klaracase, so do not add one from memory.
- Give court, decision date and Aktenzeichen for each decision, as the tool served them, and say which tool call the statement rests on.
- State what you did not read. If you only saw a search row, say you did not read the decision text.
- Do not turn a reported decision into legal advice. Describe what the sources hold and where they disagree.

## When the call is refused

- `text_too_long`: send the user to the web app Citation Check.
- `not_german_legal_text`: ask for more of the surrounding text, or check the single citation with `get_decision` or `get_norm`.
- Text under 50 characters, or a `reference_date` that is not a calendar day: fix the argument and retry. On MCP these come back as prose without an error code. On REST they are `validation_failed`.
- `insufficient_credits`, `unauthenticated`, `no_billable_organization`, `token_ability_missing`: pass on the `message` (REST: `detail`). It says what the user has to do.
- `rate_limited`: wait the stated `retry_after_seconds`, then retry once. Nothing ran and nothing was charged. A rate limit says nothing about the citations.
- `backend_unavailable`: the check did not run. Tell the user, and do not report it as a result.

REST error shapes and the curl call: `references/rest.md`.
