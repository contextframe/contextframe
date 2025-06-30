Extract comprehensive documentation using Firecrawl: $ARGUMENTS

<ultrathink>
Intelligent crawling. Structure extraction. Practical artifacts for development.
</ultrathink>

<megaexpertise type="documentation-engineer">
The assistant should demonstrate Firecrawl MCP mastery, perform deep crawl, extract patterns, and generate actionable docs.
</megaexpertise>

<context>
Documentation source: $ARGUMENTS
Transform into practical development resource
</context>

<requirements>
- Site structure analysis and navigation mapping
- Deep crawl with deduplication
- Structured information extraction
- Code examples with context
- Configuration and error handling
- LLM-friendly output generation
</requirements>

<actions parallel="true">
1. mcp_firecrawl.firecrawl_scrape(url="$ARGUMENTS", formats=["markdown", "links"]) → analyze structure
2. mcp_firecrawl.firecrawl_crawl(url="$ARGUMENTS", maxDepth=3, limit=100, deduplicateSimilarURLs=true)
3. mcp_firecrawl.firecrawl_extract(urls=[key sections], schema={endpoints, auth, examples, config, errors})
4. mcp_firecrawl.firecrawl_batch_scrape(urls=[essential pages], options={onlyMainContent: true})
5. mcp_firecrawl.firecrawl_search(query="$ARGUMENTS authentication OAuth JWT", limit=10)
6. mcp_firecrawl.firecrawl_generate_llmstxt(url="$ARGUMENTS", maxUrls=50, showFullText=true)
7. Organize in `.claude/docs/[source]/`: index, quick-start, api/, examples/, config, troubleshooting
8. Extract all code examples with use cases
9. Create integration guide tailored to our stack
10. Set up monitoring for updates
11. Output to `.claude/docs/$ARGUMENTS/` directory as a markdown file
</actions>

The assistant should create comprehensive, practical documentation package that accelerates development and makes it immediately useful.

Take a deep breath in, count 1... 2... 3... and breathe out. The assistant is now centered and should not hold back but give it their all.

