# Claude Code Meta Prompts Library

A collection of pre-built prompts for working with Claude Code in a meta way. These prompts help you use Claude to work more effectively with Claude Code itself.

## Table of Contents

1. [Project Setup & Configuration](#project-setup--configuration)
2. [Code Analysis & Understanding](#code-analysis--understanding)
3. [Development Workflows](#development-workflows)
4. [Testing & Quality](#testing--quality)
5. [Documentation](#documentation)
6. [Performance & Optimization](#performance--optimization)
7. [Debugging & Troubleshooting](#debugging--troubleshooting)
8. [Automation & Scripting](#automation--scripting)
9. [Team Collaboration](#team-collaboration)
10. [Self-Improvement](#self-improvement)

## Project Setup & Configuration

### Initialize CLAUDE.md

```
Create a comprehensive CLAUDE.md file for this project that includes:
1. Project overview and purpose
2. Development environment setup
3. Code standards and conventions
4. Testing guidelines
5. Common commands
6. Architecture decisions
7. Workflow preferences
8. Any project-specific instructions Claude should follow
```

### Generate Custom Commands

```
Analyze this codebase and create custom slash commands in .claude/commands/ for:
1. Common development tasks
2. Code quality checks
3. Testing workflows
4. Documentation generation
5. Deployment processes
Include descriptions and example usage for each command
```

### Configure MCP Servers

```
Help me set up MCP (Model Context Protocol) servers for this project:
1. Identify what external tools would be useful
2. Create the configuration in claude_config.json
3. Document how to use each MCP server
4. Create example workflows using the MCP tools
```

## Code Analysis & Understanding


### Architecture Overview
```
think about the architecture of this codebase and provide:
1. High-level architecture diagram (as text/ASCII art)
2. Key components and their responsibilities
3. Data flow between components
4. External dependencies and integrations
5. Architectural patterns used
6. Potential areas for improvement
```

### Codebase Health Check

```
Perform a comprehensive health check of this codebase:
1. Code quality metrics
2. Test coverage analysis
3. Documentation completeness
4. Security vulnerabilities
5. Performance bottlenecks
6. Technical debt assessment
7. Dependency audit
Provide a prioritized action plan for improvements
```

### Design Pattern Analysis

```
Analyze the design patterns used in this codebase:
1. Identify all design patterns present
2. Evaluate their implementation quality
3. Suggest where patterns could be better applied
4. Identify anti-patterns that should be refactored
5. Create examples of proper pattern usage
```

## Development Workflows


### Feature Implementation Workflow
```
Create a complete workflow for implementing the feature: [FEATURE_NAME]
1. Analyze requirements and edge cases
2. Design the solution architecture
3. Create a task breakdown
4. Write tests first (TDD approach)
5. Implement the feature incrementally
6. Refactor for clarity and performance
7. Update documentation
8. Create a PR with proper description
```

### Refactoring Workflow

```
think harder about refactoring this code:
1. Identify code smells and issues
2. Prioritize refactoring opportunities by impact
3. Create a safe refactoring plan
4. Write tests to ensure behavior preservation
5. Perform incremental refactoring
6. Verify no regressions occurred
7. Document the improvements made
```

### Bug Fix Workflow

```
Help me fix this bug: [BUG_DESCRIPTION]
1. Reproduce the issue reliably
2. think about potential root causes
3. Create hypotheses ranked by probability
4. Write tests that expose the bug
5. Implement the minimal fix
6. Verify the fix doesn't break other features
7. Add regression tests
8. Document the fix and prevention strategies
```

## Testing & Quality


### Comprehensive Test Suite
```
Generate a comprehensive test suite for [COMPONENT/FEATURE]:
1. Unit tests with edge cases
2. Integration tests
3. End-to-end tests
4. Performance tests
5. Security tests
6. Error handling tests
7. Mock/stub strategies
Include test descriptions and rationale
```

### Test Coverage Analysis

```
Analyze test coverage and create a plan to improve it:
1. Identify untested code paths
2. Prioritize based on code criticality
3. Generate tests for high-priority areas
4. Focus on meaningful coverage, not just percentages
5. Create a coverage report
6. Set up continuous coverage monitoring
```

### Code Quality Improvement

```
Improve the code quality of this module/file:
1. Apply SOLID principles
2. Improve naming and readability
3. Extract complex logic into functions
4. Add proper error handling
5. Optimize performance
6. Add comprehensive documentation
7. Ensure consistent code style
```

## Documentation


### API Documentation
```
Generate comprehensive API documentation:
1. Document all endpoints/methods
2. Include parameter descriptions and types
3. Provide example requests/responses
4. Document error codes and handling
5. Create usage examples
6. Generate OpenAPI/Swagger specs if applicable
7. Include authentication/authorization details
```

### Developer Guide

```
Create a developer guide for new team members:
1. Project setup instructions
2. Development workflow
3. Code style guide with examples
4. Testing practices
5. Debugging tips
6. Common issues and solutions
7. Resources for learning more
```

### Architecture Decision Records

```
Create Architecture Decision Records (ADRs) for:
1. Major technology choices
2. Architectural patterns
3. Third-party service selections
4. Performance trade-offs
5. Security decisions
Include context, decision, and consequences for each
```

## Performance & Optimization


### Performance Analysis
```
think more about performance optimization opportunities:
1. Profile the application
2. Identify performance bottlenecks
3. Analyze algorithm complexity
4. Check for memory leaks
5. Review database queries
6. Examine network requests
7. Create a prioritized optimization plan
```

### Optimization Implementation

```
Optimize this code for performance:
1. Analyze current performance metrics
2. Identify optimization opportunities
3. Implement optimizations incrementally
4. Measure impact of each change
5. Ensure no functionality regression
6. Document performance improvements
7. Create performance benchmarks
```

### Scalability Review

```
Review this application for scalability:
1. Identify scalability bottlenecks
2. Analyze concurrent request handling
3. Review data storage strategies
4. Examine caching opportunities
5. Suggest architectural improvements
6. Create a scalability roadmap
```

## Debugging & Troubleshooting


### Complex Bug Investigation
```
think harder about this complex bug:
1. Gather all available information
2. Create a timeline of when it occurs
3. Identify patterns and correlations
4. Generate multiple hypotheses
5. Design experiments to test each hypothesis
6. Implement diagnostic logging
7. Create a systematic debugging plan
```

### Error Pattern Analysis

```
Analyze error patterns in the logs/codebase:
1. Identify recurring errors
2. Categorize errors by type and severity
3. Find root causes for each category
4. Create error handling strategies
5. Implement proper error recovery
6. Add monitoring and alerting
7. Document troubleshooting procedures
```

### Memory Leak Detection

```
Help me find and fix memory leaks:
1. Identify potential leak sources
2. Add memory profiling
3. Create tests to expose leaks
4. Analyze memory growth patterns
5. Implement fixes
6. Verify leak resolution
7. Add preventive measures
```

## Automation & Scripting


### CI/CD Pipeline Creation
```
Create a comprehensive CI/CD pipeline:
1. Set up automated testing
2. Configure code quality checks
3. Implement security scanning
4. Add performance benchmarks
5. Create deployment automation
6. Set up monitoring and rollback
7. Document the pipeline
```

### Development Automation

```
Create automation scripts for common tasks:
1. Project setup and initialization
2. Database migrations
3. Test data generation
4. Deployment procedures
5. Backup and restore
6. Performance monitoring
7. Log analysis
Include error handling and logging
```

### Claude Code Automation

```
Create automated workflows using Claude Code:
1. Daily code quality reports
2. Automated refactoring suggestions
3. Test generation for new code
4. Documentation updates
5. Dependency updates and testing
6. Security vulnerability scanning
Use headless mode and Unix pipelines
```

## Team Collaboration


### Code Review Checklist
```
Create a comprehensive code review checklist:
1. Functionality requirements
2. Code quality standards
3. Testing completeness
4. Performance considerations
5. Security implications
6. Documentation requirements
7. Architectural alignment
Format as a reusable template
```

### Knowledge Sharing System

```
Set up a knowledge sharing system:
1. Document common patterns and solutions
2. Create a troubleshooting guide
3. Build a component library
4. Establish best practices
5. Create learning resources
6. Set up regular knowledge sessions
7. Build a searchable knowledge base
```

### Team Workflow Optimization

```
Analyze and optimize our team workflow:
1. Review current development process
2. Identify bottlenecks and inefficiencies
3. Suggest process improvements
4. Create workflow automation
5. Establish clear responsibilities
6. Improve communication channels
7. Measure workflow improvements
```

## Self-Improvement


### Claude Usage Analysis
```
Analyze how I'm using Claude Code and suggest improvements:
1. Review my prompt patterns
2. Identify inefficient workflows
3. Suggest better prompting strategies
4. Recommend useful features I'm not using
5. Create personalized commands
6. Optimize for my specific needs
```

### Learning Path Generation

```
Create a learning path for improving my skills with:
1. Current skill assessment
2. Gap analysis
3. Prioritized learning objectives
4. Resource recommendations
5. Practice exercises
6. Progress milestones
7. Real-world application projects
```

### Productivity Metrics

```
Help me track and improve my development productivity:
1. Define meaningful metrics
2. Create tracking mechanisms
3. Analyze productivity patterns
4. Identify improvement areas
5. Suggest workflow optimizations
6. Create productivity dashboards
7. Set and track goals
```

## Meta-Prompt Templates


### Custom Prompt Generator
```
Create custom prompts for my specific use case: [USE_CASE]
1. Analyze the requirements
2. Create prompt templates
3. Include variable placeholders
4. Add example usage
5. Create variations for different scenarios
6. Test and refine prompts
7. Document best practices
```

### Prompt Optimization

```
Optimize this prompt for better results: [ORIGINAL_PROMPT]
1. Analyze the current prompt
2. Identify ambiguities or inefficiencies
3. Apply prompt engineering best practices
4. Create multiple variations
5. Test each variation
6. Select the best performer
7. Document the improvements
```

### Workflow Prompt Chains

```
Create a chain of prompts for this workflow: [WORKFLOW]
1. Break down the workflow into steps
2. Create prompts for each step
3. Ensure proper context passing
4. Add decision points
5. Include error handling
6. Create automation scripts
7. Document the complete chain
```

## Advanced Meta Techniques


### Multi-Claude Orchestration
```
Design a multi-Claude workflow for: [COMPLEX_TASK]
1. Decompose the task into parallel work
2. Assign specialized roles to each instance
3. Define communication protocols
4. Create synchronization points
5. Implement result aggregation
6. Handle failures gracefully
7. Document the orchestration
```

### Recursive Self-Improvement

```
Create a recursive improvement system:
1. Analyze current codebase state
2. Generate improvement suggestions
3. Implement top suggestions
4. Measure improvements
5. Learn from results
6. Generate new suggestions based on learnings
7. Repeat until optimal
```

### AI-Assisted Architecture

```
Help me design an AI-friendly architecture:
1. Analyze current limitations for AI assistance
2. Suggest architectural patterns that work well with AI
3. Create clear boundaries and interfaces
4. Design for testability and observability
5. Enable easy AI-driven refactoring
6. Build in self-documentation
7. Create AI-optimized workflows
```

## Usage Tips


1. **Combine Prompts**: Mix and match prompts for complex tasks
2. **Customize Variables**: Replace placeholders with your specific needs
3. **Iterate Results**: Use "think harder" or "think more" for deeper analysis
4. **Save Successful Prompts**: Add working prompts to your .claude/commands
5. **Version Control**: Track prompt evolution in your repository
6. **Team Sharing**: Share effective prompts with your team
7. **Continuous Improvement**: Refine prompts based on results

Remember: The best prompts are specific, contextual, and iterative. Start with these templates and refine them for your unique needs.
