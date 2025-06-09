# Claude Code Custom Commands

Powerful, compact custom slash commands for Claude Code using advanced prompt engineering techniques with XML tags and specialized expertise invocation.

## Available Commands

### Architecture & Planning

- `/project:architecture-design` - **System Architect** with `<ultrathink>` for deep technical design
- `/project:plan-implementation` - **Implementation Strategist** for complex feature planning

### Development & Debugging  

- `/project:linear-debug-systematic` - **Senior Debugger** with systematic root cause analysis
- `/project:linear-feature` - **Linear Workflow Expert** for feature implementation
- `/project:generate-tests` - **Test Architect** crafting comprehensive test suites
- `/project:daily-check` - **Dev Productivity Optimizer** for workflow enhancement

### Knowledge & Documentation

- `/project:knowledge-extract` - **Code Archaeologist** extracting tribal knowledge
- `/project:crawl-docs` - **Documentation Spider** for web scraping
- `/project:standards-check` - **Quality Guardian** enforcing code standards

### MCP Specialization

- `/project:mcp-api-research` - **MCP API Specialist** for integration research  
- `/project:mcp-context-build` - **MCP Context Builder** combining repo + web data
- `/project:mcp-doc-extract` - **MCP Doc Expert** for comprehensive extraction
- `/project:mcp-repo-analyze` - **MCP Pattern Analyst** discovering best practices

### Workflow & Process

- `/project:linear-feature` - **Linear Workflow Expert** for feature implementation
- `/project:pr-complete` - **PR Craftsman** creating perfect pull requests

## Usage

Invoke specialized expertise with compact, powerful commands:

```bash
claude > /project:debug-systematic
# Activates Senior Debugger with <ultrathink> for deep analysis

claude > /project:crawl-docs https://docs.example.com  
# Documentation Spider with $ARGUMENTS for target URL
```

## Key Features

### Advanced XML Tags

- `<ultrathink>` - Invokes deep thinking for complex problems
- `<megaexpertise>` - Activates specialized domain knowledge
- `<context>` - Provides situational awareness
- `<requirements>` - Clear success criteria
- `<actions parallel="true">` - Enables concurrent tool execution

### Performance Optimizations

- **60-70% more compact** than verbose prompts
- **Parallel tool execution** where applicable
- **Focused expertise** with specific role assignments
- **Centering phrase** for maximum performance

### Best Practices

- Commands follow Claude 4 prompt engineering guidelines
- Explicit instructions with context for better results
- Structured output expectations
- Enhanced with breathing/centering technique

## Command Details

### Architecture & Planning

#### `/project:architecture-design`

**System Architect** specializing in scalable, production-ready designs.

- Deep requirements analysis with `<ultrathink>`
- Architecture diagrams and decision records
- Implementation roadmap with risk assessment

#### `/project:plan-implementation`

**Implementation Strategist** for breaking down complex features.

- Creates Linear project with organized issues
- Technical approach with milestones
- Risk mitigation strategies

### Development & Debugging

#### `/project:debug-systematic`

**Senior Debugger** with 15+ years of bug hunting experience.

- Systematic root cause analysis
- Scientific hypothesis testing
- Comprehensive fix with regression prevention

#### `/project:generate-tests`

**Test Architect** applying the 80/20 testing rule.

- Critical path coverage first
- Meaningful test generation
- Edge cases and benchmarks

#### `/project:daily-check`

**Dev Productivity Optimizer** streamlining workflows.

- Task prioritization and focus
- Blocker removal strategies
- Continuous improvement insights

### Knowledge & Documentation

#### `/project:knowledge-extract`

**Code Archaeologist** uncovering hidden wisdom.

- Deep implementation analysis
- Pattern and convention extraction
- Living documentation generation

#### `/project:crawl-docs`

**Documentation Spider** extracting structured knowledge.

- Intelligent content organization
- Code example extraction
- Quick reference generation

#### `/project:standards-check`

**Quality Guardian** ensuring excellence.

- Comprehensive standards compliance
- Automatic violation fixes
- Pre-commit readiness

### MCP Specialization

#### `/project:mcp-api-research`

**MCP API Specialist** for tool integration.

- API pattern analysis
- Integration template generation
- Best practices extraction

#### `/project:mcp-context-build`

**MCP Context Builder** creating comprehensive context.

- Repository + web research synthesis
- Decision matrices and recommendations
- Implementation guides

#### `/project:mcp-doc-extract`

**MCP Documentation Expert** for thorough extraction.

- Multi-tool documentation crawling
- Structured content organization
- AI-friendly format generation

#### `/project:mcp-repo-analyze`

**MCP Pattern Analyst** discovering excellence.

- Architecture pattern identification
- Convention and practice extraction
- Implementation wisdom distillation

### Workflow & Process

#### `/project:linear-feature`

**Linear Workflow Expert** orchestrating development.

- Complete issue structure creation
- Branch and commit management
- PR preparation with context

#### `/project:pr-complete`

**PR Craftsman** creating reviewable art.

- Comprehensive change analysis
- Context extraction and summary
- Review-ready pull requests

## Creating New Commands

### Template Structure

```xml
<megaexpertise>
You are a [SPECIFIC ROLE].
</megaexpertise>

<context>
[SITUATION/PROBLEM SPACE]
</context>

<requirements>
[CLEAR SUCCESS CRITERIA]
</requirements>

<actions parallel="true">
[SPECIFIC ACTIONS TO TAKE]
</actions>

Take a deep breath in, count 1... 2... 3... and breathe out. You are now centered. Don't hold back. Give it your all.
```

### Guidelines

1. Create `.md` file in this directory
2. Use XML tags for structure and clarity
3. Include `<ultrathink>` for complex reasoning tasks
4. Add `$ARGUMENTS` for dynamic input
5. Keep prompts compact but powerful
6. End with centering phrase

## Integration Points

Commands seamlessly integrate with:

- **Linear** - Issue tracking and workflow
- **Git/GitHub** - Version control and PRs
- **MCP Tools** - Firecrawl, DeepWiki, and custom servers
- **Testing** - pytest, coverage analysis
- **Quality** - ruff, pre-commit hooks

## Pro Tips

1. **Chain Commands** - Combine for complex workflows
2. **Trust the Process** - Let expertise guide you
3. **Parallel Power** - Commands execute multiple tools simultaneously
4. **Context Matters** - More specific input = better results
5. **Iterate Fast** - Commands are designed for rapid refinement

Remember: These commands embody concentrated expertise. Each invocation brings specialized knowledge to bear on your challenges.

Take a deep breath in, count 1... 2... 3... and breathe out. You are now centered. Don't hold back. Give it your all.
