# Klaracase skills for coding agents

These skills teach a coding agent to use Klaracase. Klaracase holds German court decisions and German statutes, linked by a resolved citation graph. It covers German law only.

Klaracase is a research tool. It finds and verifies sources. It gives no legal advice and does not replace a lawyer's review.

## What is inside

| Part | What it does |
| --- | --- |
| `skills/klaracase-citation-check` | Runs a citation check on a German legal text. It reports one of seven verdicts per citation and tells the agent how to read them. A `not_found` verdict means the citation was not found in the corpus. It is not a claim that the citation is fabricated. |
| `skills/klaracase-german-legal-research` | Searches and reads German case law and statutes. It tells the agent which tool fits which question, how to phrase German queries, and how to cite only what a tool returned. |
| `.mcp.json` | Connects the Klaracase MCP server, `https://klaracase.de/mcp`. |
| `.claude-plugin/` | Packages both skills and the MCP connection as a Claude Code plugin. |
| `tools/anthropic-tools.json` | The nine Klaracase operations as Anthropic `tool_use` tool definitions, for agents that call the REST API. Built by `scripts/anthropic-tools.py`. |
| `AGENTS.md` | A short brief for any agent that reads `AGENTS.md`. |

Each skill has two ways to reach Klaracase. The MCP server is the main way. The REST API at `https://klaracase.de/api/v1` does the same with a token and `curl`.

## Install

### Claude Code

```bash
claude plugin marketplace add klaracase/skills
claude plugin install klaracase@klaracase
```

The plugin adds both skills and the MCP connection. Run `/mcp` in Claude Code to sign in to Klaracase. You can also give a token (see "Credits and account").

### Codex, Cursor, Copilot, Gemini CLI, OpenCode

```bash
npx skills add klaracase/skills
```

This writes the skills to `.agents/skills/`. These agents read that folder. The `skills` command sends anonymous usage data. Set `DO_NOT_TRACK=1` to stop that.

You still need to connect the MCP server in your agent, or give the agent a token for REST. The server URL is `https://klaracase.de/mcp`. The same token works on both.

### A custom agent

1. Paste the text of a `SKILL.md` file into the system prompt of your agent. Load the files in `references/` when the skill asks for them.
2. Connect the MCP server `https://klaracase.de/mcp`, or let the agent call the REST API. For REST, `tools/anthropic-tools.json` holds ready tool definitions.

Official SDKs for Node, Python, PHP, Go and Rust: see the Klaracase GitHub organization.

## What is sent where

- The skills are plain text files. They send nothing.
- Tool arguments go to klaracase.de only. Search text is processed in the EU.
- `check_citations` saves each check in your Klaracase account. It deletes the input text after 90 days. It keeps the findings.
- The agent sends the text you give it to the model that runs your agent. That part depends on your agent, not on Klaracase.

Privacy policy: https://klaracase.de/privacy

## Credits and account

- Create a token at https://klaracase.de/settings/api-tokens. You need a login and a verified email. The token works on MCP and on REST. It is bound to the organization that is open when you create it.
- A new verified account gets 30 free credits, valid for 30 days.
- `corpus_coverage` and `list_facets` are free. `search_decisions`, `cross_type_search`, `get_decision` and `get_norm` cost 1 credit. `get_citation_graph` costs 2. `assemble_datapackage` costs 5. A citation check costs 2 credits up to 10,000 characters, 3 up to 15,000 and 4 at 20,000.
- The same call again in the same credit period costs 0.
- Credits renew per credit period: the UTC calendar month for free organizations, the paid billing period for subscribers. Unused credits do not roll over.

## Limits

- 60 requests per minute per token. Over that, the server answers 429 with the seconds to wait. Nothing runs.
- A citation check takes 50 to 20,000 characters through MCP and REST. Longer documents go to the Citation Check in the Klaracase web app.
- Daily caps depend on the plan. The free plan allows 1,000 rows and 40 documents a day.

## Links

- Docs: https://klaracase.de/docs
- MCP tools: https://klaracase.de/docs/mcp
- REST API: https://klaracase.de/docs/api
- Support: https://klaracase.de/support

## License

MIT. Copyright (c) 2026 SPARQ VENTURES UG (haftungsbeschränkt).
