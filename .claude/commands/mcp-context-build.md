Build comprehensive development context: $ARGUMENTS

<ultrathink>
Combine DeepWiki repository analysis + Firecrawl web research. Maximum context for informed decisions.
</ultrathink>

<megaexpertise type="research-analyst">
The assistant should perform multi-source intelligence gathering including internal patterns, external best practices, and implementation examples.
</megaexpertise>

<context>
Building context for: $ARGUMENTS
Could be new tech, feature, problem, or architecture decision
</context>

<requirements>
- Internal codebase analysis (our patterns, similar solutions)
- External documentation research (official docs, best practices)
- Open source implementation examples
- Technical specifications and constraints
- Problem domain understanding
- Decision matrix with trade-offs
- Implementation guidance
</requirements>

<actions parallel="true">
Internal Analysis:
1. mcp_deepwiki.ask_question(repo="[our-repo]", question="How is $ARGUMENTS implemented/used? Include patterns.")
2. mcp_deepwiki.ask_question(repo="[our-repo]", question="What similar solutions exist?")

External Research:
3. mcp_firecrawl.firecrawl_deep_research(query="$ARGUMENTS best practices implementation guide", maxDepth=3, maxUrls=100)
4. mcp_firecrawl.firecrawl_search(query="$ARGUMENTS implementation example github production", limit=20)
5. For found repos: mcp_deepwiki.ask_question(repo="[found-repo]", question="How is $ARGUMENTS implemented? Patterns? Best practices?")
6. mcp_firecrawl.firecrawl_extract(urls=["[docs-url]"], prompt="Extract specifications, requirements, constraints, best practices")

Synthesis:
7. Research problem domain and alternatives
8. Build decision matrix from findings
9. Create implementation guide based on context
10. Extract lessons learned from others
11. Generate `.claude/context/$ARGUMENTS/` package
12. Create LLM-friendly reference: mcp_firecrawl.firecrawl_generate_llmstxt()
13. Output to `.claude/context/$ARGUMENTS/` directory as a markdown file
</actions>

The assistant should combine repository wisdom with web intelligence and build context that accelerates development and improves decisions.

Take a deep breath in, count 1... 2... 3... and breathe out. The assistant is now centered and should not hold back but give it their all.
