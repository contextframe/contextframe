# Claude Code Meta Standards

This document provides comprehensive standards and best practices for working with Claude Code in a meta way - using Claude to help work with Claude Code itself.

## Core Workflow Patterns

### 1. Explore → Plan → Code → Commit Pattern
The recommended workflow for any development task:

```bash
# 1. Explore: Understand the codebase
"Show me the architecture of this project"
"What are the key components and how do they interact?"
"Find all files related to [feature]"

# 2. Plan: Create a detailed plan
"Create a plan for implementing [feature]"
"What edge cases should we consider?"
"How should we structure the tests?"

# 3. Code: Implement with verification
"Implement the planned solution"
"Run the tests and fix any issues"
"Verify the code follows project standards"

# 4. Commit: Create meaningful commits
"Create a commit with a descriptive message"
"Create a PR following the project conventions"
```

### 2. Test-Driven Development Pattern
For robust implementations:

```bash
# 1. Write tests first
"Write comprehensive tests for [feature]"
"Include edge cases and error scenarios"

# 2. Verify tests fail
"Run the tests and confirm they fail"

# 3. Implement minimal code to pass
"Implement just enough code to make the tests pass"

# 4. Refactor and optimize
"Refactor the implementation for clarity and performance"
```

## Extended Thinking Techniques

### When to Use Extended Thinking
- Complex architectural decisions
- Debugging intricate issues
- Performance optimization
- Security analysis
- Code review and refactoring strategies

### Thinking Levels
1. **Basic**: Default reasoning
2. **Think**: `"think about this problem"`
3. **Think Hard**: `"think harder about the edge cases"`
4. **Think More**: `"think more about the performance implications"`
5. **Ultrathink**: For extremely complex problems requiring deep analysis

### Example Prompts
```bash
# Architecture decisions
"think about the best architecture for this feature"

# Debugging
"think harder about why this bug might be occurring"

# Optimization
"think more about how to optimize this algorithm"
```

## Meta-Programming with Claude Code

### 1. Creating Custom Commands
Store frequently used prompts and workflows:

```bash
# In .claude/commands/
refactor:
  description: "Refactor code following best practices"
  prompt: |
    Refactor the selected code to:
    1. Improve readability
    2. Follow project conventions
    3. Optimize performance
    4. Add proper error handling
    5. Include comprehensive tests

test-coverage:
  description: "Analyze and improve test coverage"
  prompt: |
    1. Identify untested code paths
    2. Generate tests for uncovered areas
    3. Include edge cases and error scenarios
    4. Verify all tests pass
```

### 2. Project-Specific Instructions (CLAUDE.md)
Essential sections to include:

```markdown
# CLAUDE.md

## Project Overview
[Brief description of the project and its purpose]

## Development Environment
- Required tools and versions
- Setup commands
- Environment variables

## Code Standards
- Style guide preferences
- Naming conventions
- File organization
- Import ordering

## Testing Guidelines
- Test framework and commands
- Coverage requirements
- Test file naming
- Mock/stub conventions

## Common Commands
- Build: `npm run build`
- Test: `npm test`
- Lint: `npm run lint`
- Deploy: `npm run deploy`

## Architecture Decisions
- Key patterns used
- Technology choices
- Performance considerations

## Workflow Preferences
- Branch naming
- Commit message format
- PR process
- Code review checklist
```

### 3. Multi-Claude Workflows
For complex tasks requiring parallel work:

```bash
# Terminal 1: Frontend development
cd frontend && claude --continue
"Implement the new user interface components"

# Terminal 2: Backend development
cd backend && claude --continue
"Create the API endpoints for the new feature"

# Terminal 3: Testing and integration
claude --continue
"Write integration tests for the frontend and backend"
```

## Automation and Scripting

### 1. Headless Mode Usage
For automated workflows:

```bash
# Generate documentation
claude --no-interaction "Generate API documentation from the codebase" > api-docs.md

# Code analysis
claude --print "Analyze code quality and suggest improvements" | tee analysis.txt

# Automated refactoring
claude --continue --no-interaction "Refactor all deprecated patterns"
```

### 2. Unix Pipeline Integration
```bash
# Find and fix issues
find . -name "*.js" | claude --print "Review these files for security issues"

# Generate reports
git diff | claude "Summarize these changes for the changelog"

# Batch processing
ls src/**/*.ts | claude "Generate tests for each of these files"
```

## Visual Context Best Practices

### 1. When to Use Images
- UI/UX design discussions
- Error screenshots
- Architecture diagrams
- Schema visualizations
- Performance graphs

### 2. Effective Image Usage
```bash
# Drag and drop or paste images directly
"Here's the design mockup [paste image]. Implement this interface"

# Reference local images
"Analyze this error screenshot: /path/to/screenshot.png"

# Multiple images for comparison
"Compare these two UI designs and suggest improvements"
```

## Performance Optimization

### 1. Context Management
- Use `/clear` to reset context when switching tasks
- Be specific to reduce token usage
- Summarize long conversations before continuing

### 2. Efficient Prompting
```bash
# Bad: Vague and open-ended
"Fix the code"

# Good: Specific and actionable
"Fix the null pointer exception in UserService.authenticate() by adding proper validation"

# Bad: Multiple unrelated tasks
"Fix bugs, add tests, update docs, and deploy"

# Good: Focused single task
"Add unit tests for the UserService class with 90% coverage"
```

## Safety and Security

### 1. Tool Permissions
Configure carefully in settings:
- **Read**: Generally safe for all projects
- **Write**: Enable for trusted projects only
- **Execute**: Use with extreme caution
- **Delete**: Typically keep disabled

### 2. Code Review Practices
```bash
# Before accepting changes
"Show me all the changes you're about to make"
"Explain the security implications of this code"
"Are there any potential side effects?"
```

## Common Meta-Patterns

### 1. Self-Improvement Loop
```bash
# Analyze current code
"Analyze this codebase and identify improvement opportunities"

# Generate improvement plan
"Create a prioritized plan for addressing these issues"

# Implement improvements
"Implement the top 3 improvements from the plan"

# Verify improvements
"Measure the impact of these changes"
```

### 2. Knowledge Transfer
```bash
# Document tribal knowledge
"Interview me about this codebase and create documentation"

# Generate onboarding guides
"Create an onboarding guide for new developers"

# Create architectural decision records
"Document the key architectural decisions in this project"
```

### 3. Continuous Learning
```bash
# Learn from patterns
"Identify the design patterns used in this codebase"

# Apply learnings
"Apply these patterns to the new feature"

# Document learnings
"Create a patterns guide based on what we've learned"
```

## Advanced MCP Integration

### 1. Custom MCP Servers
For project-specific tools:
```json
{
  "mcpServers": {
    "project-tools": {
      "command": "node",
      "args": ["./mcp-server/index.js"],
      "type": "stdio"
    }
  }
}
```

### 2. MCP Best Practices
- Keep servers lightweight
- Handle errors gracefully
- Document server capabilities
- Version server protocols

## Debugging Strategies

### 1. Systematic Debugging
```bash
# 1. Reproduce the issue
"Help me create a minimal reproduction of this bug"

# 2. Analyze root cause
"think hard about what could cause this behavior"

# 3. Generate hypotheses
"List possible causes ranked by probability"

# 4. Test hypotheses
"Create tests to verify each hypothesis"

# 5. Implement fix
"Implement the fix for the confirmed root cause"
```

### 2. Performance Debugging
```bash
# Profile the code
"Add performance monitoring to identify bottlenecks"

# Analyze results
"think about optimization strategies for these bottlenecks"

# Implement optimizations
"Implement the most impactful optimizations"

# Verify improvements
"Measure the performance improvements"
```

## Team Collaboration

### 1. Shared Standards
Create team-wide command sets:
```bash
# .claude/commands/team-standards
code-review:
  prompt: "Review this code against our team standards checklist"

pr-prep:
  prompt: "Prepare this code for PR: lint, test, document"
```

### 2. Knowledge Sharing
```bash
# Document solutions
"Document how we solved this problem for future reference"

# Create examples
"Create example code demonstrating this pattern"

# Generate FAQs
"Create an FAQ based on common issues in this codebase"
```

## Conclusion

These standards provide a foundation for using Claude Code effectively in a meta way. The key principles are:

1. **Be Specific**: Clear, actionable prompts yield better results
2. **Think Strategically**: Use extended thinking for complex problems
3. **Automate Wisely**: Leverage headless mode and scripting
4. **Document Everything**: Maintain CLAUDE.md and custom commands
5. **Iterate Continuously**: Refine your approach based on results

Remember: The best workflow is the one that works for your specific needs. Experiment with these patterns and adapt them to your project's requirements.