Analyze repository using DeepWiki: $ARGUMENTS

<ultrathink>
Extract patterns, solutions, wisdom. Learn from their code to improve ours.
</ultrathink>

<megaexpertise type="code-analyst">
DeepWiki AI-powered analysis. Understand architecture, patterns, decisions. Extract reusable wisdom.
</megaexpertise>

<context>
Repository to analyze: $ARGUMENTS
Extract actionable insights for our development
</context>

<requirements>
- Documentation structure and core concepts
- Architectural patterns and design decisions
- Code conventions and best practices
- Problem solutions and approaches
- Testing and quality strategies
- Reusable components and utilities
- Security measures and performance tactics
</requirements>

<actions>
1. mcp_deepwiki.read_wiki_structure(repo="$ARGUMENTS") → map available docs
2. Read core docs: architecture, API, contributing
3. Ask targeted questions:
   - "Main architectural patterns? Service boundaries, data flow, key decisions?"
   - "Coding patterns? Error handling, testing strategies, utilities?"
   - "Performance optimization? Caching, database, scaling?"
   - "Interesting problem solutions? Auth, validation, API design?"
   - "Testing strategy? Structure, mocking, coverage, CI/CD?"
   - "Reusable components? Purpose and implementation?"
   - "Development workflow? Branches, reviews, deployment?"
   - "Security practices? Auth, data protection, validation?"
4. Extract specific pattern implementations with file paths
5. Compare approaches with common practices
6. Create `.claude/learning/[repo]/` with insights
7. Generate adoption plan: immediate wins, architecture ideas, code to extract
8. Output to `.claude/learning/$ARGUMENTS/` directory as a markdown file
</actions>

Extract maximum learning value. Focus on patterns we can apply immediately to improve our codebase.

Take a deep breath in, count 1... 2... 3... and breathe out. You are now centered. Don't hold back. Give it your all.