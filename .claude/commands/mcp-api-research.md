Deep API research using Firecrawl MCP for: $ARGUMENTS

<ultrathink>
Extract everything needed for robust integration. Authentication, endpoints, rate limits, examples, edge cases.
</ultrathink>

<megaexpertise type="api-integration-specialist">
Use Firecrawl's AI-powered extraction. Build complete API understanding for production integration.
</megaexpertise>

<context>
Researching API: $ARGUMENTS
Need comprehensive documentation for integration
</context>

<requirements>
- Complete API specification extraction
- Authentication methods and setup
- All endpoints with parameters/responses
- Rate limits and error codes
- Real-world usage examples
- SDK/library documentation
- Common issues and solutions
</requirements>

<actions parallel="true">
1. mcp_firecrawl.firecrawl_scrape(url="$ARGUMENTS", formats=["markdown", "links"])
2. mcp_firecrawl.firecrawl_deep_research(query="$ARGUMENTS API authentication endpoints rate limits error codes examples", maxDepth=3, maxUrls=75)
3. mcp_firecrawl.firecrawl_extract(urls=["$ARGUMENTS/reference", "$ARGUMENTS/auth", "$ARGUMENTS/endpoints"], schema={endpoints, authentication, rateLimits, errorCodes})
4. mcp_firecrawl.firecrawl_search(query="$ARGUMENTS API integration example Python JavaScript", limit=20)
5. mcp_firecrawl.firecrawl_batch_scrape(urls=[SDKs, libraries, quickstart])
6. Research common issues: timeout, rate limit, 401, 403 errors
7. Extract all code examples with full implementation
8. Generate API client template with retry logic, rate limiting, error handling
9. Create integration guide with checklist
10. Monitor API changes via changelog
</actions>

Build complete API understanding enabling smooth, robust integration. Generate production-ready client implementation.

Take a deep breath in, count 1... 2... 3... and breathe out. You are now centered. Don't hold back. Give it your all.