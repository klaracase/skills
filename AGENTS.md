# Klaracase skills for coding agents

This repository holds two agent skills and a Claude Code plugin for Klaracase. Klaracase holds
German court decisions and German statutes, linked by a resolved citation graph. It covers
German law only.

## Which skill answers what

- `skills/klaracase-citation-check/SKILL.md`: the user pastes a German legal text and asks
  whether its citations are real or traceable. Runs a citation check and reports one of seven
  verdicts per citation.
- `skills/klaracase-german-legal-research/SKILL.md`: the user asks what German courts decided,
  or for the text of a decision or a statute. Search, read, follow citations.

Read the matching SKILL.md before you call a Klaracase tool. Details are in each skill's
`references/` folder.

## Connect

- MCP server (streamable HTTP): `https://klaracase.de/mcp`
- REST base URL: `https://klaracase.de/api/v1`
- Token page: https://klaracase.de/settings/api-tokens. The same Bearer token works on MCP and
  on REST. Keep it in `KLARACASE_API_TOKEN`. Never write it into a file.
- Docs: https://klaracase.de/docs, https://klaracase.de/docs/mcp, https://klaracase.de/docs/api

## Credits

- Free tools: `corpus_coverage`, `list_facets`, uploads and read-backs.
- `search_decisions`, `cross_type_search`, `get_decision`, `get_norm`: 1 credit each.
- `get_citation_graph`: 2 credits. `assemble_datapackage`: 5 credits.
- `check_citations`: 2 credits up to 10,000 characters, 3 up to 15,000, 4 at 20,000.
- A repeat of the same call in the same billing period costs 0.
- A new verified account gets 30 free credits, valid for 30 days.

## The one rule

Cite only what a tool returned. Name every Aktenzeichen and norm from a tool result. A file
number that no tool returned has no source in Klaracase, so do not add one from memory.

## Not legal advice

Klaracase is a research tool. It gives no legal advice and does not replace a lawyer's review.

## Official SDKs

REST clients for Node, Python, PHP, Go and Rust live in the Klaracase GitHub organization
(`klaracase`, <https://github.com/klaracase>). Agents that need tools should use the MCP server.
