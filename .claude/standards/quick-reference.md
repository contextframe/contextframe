# Claude Code Quick Reference

Essential commands and patterns for effective Claude Code usage.

## Most Used Commands

### Basic Operations

```bash
claude --continue          # Resume last conversation
claude --resume           # Select from past conversations
claude --model claude-3.5  # Use specific model
claude --no-cache         # Start fresh conversation
/clear                    # Clear context within session
/exit                     # Exit Claude Code
```

### Thinking Modes

```bash
"think about..."          # Deeper reasoning
"think harder about..."   # Complex problem solving
"think more about..."     # Extended analysis
```

### File Operations

```bash
/read <file>              # Read specific file
/save <file>              # Save conversation
/diff                     # Show changes to be made
```

### Custom Project Commands

```bash
/project:daily-check                    # Daily development status
/project:linear-plan-implementation <feature>  # Create Linear implementation plan
/project:linear-feature <name>          # Complete feature workflow
/project:linear-debug-systematic <issue>       # Systematic debugging
/project:standards-check <path>         # Check and fix standards
/project:generate-tests <component>     # Generate comprehensive tests
/project:pr-complete                    # Create professional PR
/project:architecture-design <system>   # Design system architecture
/project:knowledge-extract <topic>      # Extract and document knowledge
/project:crawl-docs <url>              # Crawl and save documentation

# MCP-Powered Documentation Commands
/project:mcp-doc-extract <url>         # Extract docs using Firecrawl MCP
/project:mcp-repo-analyze <repo>       # Analyze repos using DeepWiki MCP
/project:mcp-api-research <api>        # Research APIs using Firecrawl MCP
/project:mcp-context-build <topic>     # Build context using both MCPs
```

## Essential Meta Prompts

### Quick Analysis

```
"Analyze this codebase and tell me the 3 most important things I should know"
```

### Fast Bug Fix

```
"Here's the error: [ERROR]. Fix it with minimal changes"
```

### Instant Test

```
"Write a test for this function that covers the main use case"
```

### Quick Refactor

```
"Refactor this code to be more readable without changing functionality"
```

### Simple Documentation

```
"Add a one-line comment explaining what this does"
```

## Power User Shortcuts

### Batch Operations

```bash
# Process multiple files
find . -name "*.py" | claude "Add type hints to all functions"

# Quick review
git diff | claude "Is this change safe to deploy?"

# Fast documentation
claude --print "List all API endpoints" > endpoints.md
```

### Workflow Accelerators

```bash
# Debug mode
"Add print statements to trace execution flow"

# Performance check
"Is there an obvious performance issue here?"

# Security scan
"Any security vulnerabilities in this code?"

# Dependency check
"What external libraries does this need?"
```

## Common Patterns

### The 3-Step Debug

1. "What does this error mean?"
2. "How do I fix it?"
3. "Verify the fix works"

### The Quick Feature

1. "Add [FEATURE] to this code"
2. "Write a test for it"
3. "Run the test"

### The Fast Review

1. "Review this code"
2. "Fix any issues you find"
3. "Explain what you changed"

## Emergency Commands

```bash
# When stuck
"Explain what's happening here in simple terms"

# When confused
"Start over. What are we trying to do?"

# When errors persist
"List all possible causes for this error"

# When nothing works
"What's the simplest solution that could work?"
```

## Time Savers

### Auto-Complete Tasks

```
"Finish implementing this function"
"Complete the TODO items in this file"
"Fill in the missing test cases"
```

### Quick Generations

```
"Generate a README for this project"
"Create a basic test file"
"Write a simple example"
```

### Instant Checks

```
"Is this code correct?"
"Will this work?"
"Any bugs here?"
```

## Pro Tips

1. **Be Direct**: Shorter prompts often work better
2. **Use Context**: Reference error messages and code directly
3. **Chain Commands**: Combine multiple operations in one prompt
4. **Trust Defaults**: Claude Code's defaults are usually optimal
5. **Iterate Fast**: Quick attempts beat perfect first tries

## Copy-Paste Templates

### Debug Template

```
Error: [PASTE ERROR]
Code: [PASTE CODE]
Fix this.
```

### Feature Template

```
Add [FEATURE] that [DOES THIS].
Keep it simple.
Test it.
```

### Review Template

```
Review and improve:
[PASTE CODE]
```

## Keyboard Shortcuts

- `Ctrl+C`: Cancel current operation
- `Up Arrow`: Previous command (in chat)
- `Tab`: Auto-complete file paths
- `Ctrl+D`: Exit Claude Code

## Remember

- **Specific > Vague**: "Fix the null pointer in line 42" > "Fix the bug"
- **Simple > Complex**: Start simple, add complexity if needed
- **Action > Discussion**: "Do X" > "What do you think about X?"
- **Now > Perfect**: Iterate quickly rather than planning extensively

---

*Keep this reference handy. The best Claude Code usage is fast, focused, and iterative.*
