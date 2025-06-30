Extract comprehensive documentation from: $ARGUMENTS

<ultrathink>
Capture every useful detail, example, pattern. Make this our definitive knowledge source.
</ultrathink>

<megaexpertise type="documentation-specialist">
The assistant should use WebFetch for intelligent content extraction, follow links, find hidden gems, and organize systematically.
</megaexpertise>

<context>
Need complete documentation extraction from: $ARGUMENTS
Will become our source of truth for development
</context>

<requirements>
- Deep content analysis with link following
- Logical organization (concepts, API, examples, troubleshooting)
- Code snippet extraction with context
- Configuration examples and patterns
- Version-specific information
- Quality verification
</requirements>

<actions>
1. WebFetch main page → identify structure and navigation
2. Extract linked pages, subpages, related docs
3. Organize by categories: Getting Started, Core Concepts, API Reference, Examples, Best Practices, Configuration, Troubleshooting, Advanced
4. Extract all code snippets with descriptions
5. Capture error messages, solutions, patterns, anti-patterns
6. Save to `.claude/documentation/[source-name]/` with metadata
7. Generate quick reference guide and cheatsheet
8. Flag outdated or conflicting information
</actions>

The assistant should create comprehensive, well-organized documentation package that accelerates development and makes it immediately useful.

Take a deep breath in, count 1... 2... 3... and breathe out. The assistant is now centered and should not hold back but give it their all.
