Create comprehensive implementation plan: $ARGUMENTS

<ultrathink>
Think deeply about requirements. Break down into actionable plan. Every detail for successful implementation.
</ultrathink>

<megaexpertise type="technical-architect">
Structured planning with Linear integration. Complete issue hierarchy with clear acceptance criteria.
</megaexpertise>

<context>
Planning implementation for: $ARGUMENTS
Need detailed, actionable plan with measurable outcomes
</context>

<requirements>
- Extract all requirements (functional, non-functional, constraints)
- Consider edge cases and error scenarios
- Create Linear issue hierarchy
- Define acceptance criteria
- Include time estimates with buffer
- Map dependencies
- Assess risks
</requirements>

<actions>
1. Analyze requirements thoroughly → extract explicit and implicit needs
2. Check for existing projects → mcp_linear.list_projects(teamId, includeArchived=false)
3. Create or use project → mcp_linear.create_project(name="[Feature] $ARGUMENTS", description="Implementation tracking")
4. Create comprehensive issues within project:
   - Architecture & Design Issue: Technical design, data models, API contracts
   - Core Implementation Issue: Complete functionality with detailed breakdown
   - Error Handling Issue: Comprehensive scenarios and recovery strategies
   - Testing Strategy Issue: Unit, integration, e2e test plans
   - Documentation Issue: API docs, user guides, technical documentation
   - Performance Issue: Benchmarks, optimization strategies, monitoring
   - Security Issue: Auth implementation, validation, data protection
5. Each issue includes: 
   - Detailed scope and requirements
   - Acceptance criteria checklist
   - Time estimate with buffer
   - Dependencies clearly mapped
   - Technical implementation notes
   - Links to project for context
6. Generate workflow: branch names per issue, implementation order, commit templates, PR checklist
7. Output summary: project URL, issue list with IDs, implementation order, risk assessment, success metrics
</actions>

This plan guides entire implementation. Be thorough, specific, actionable. Include all technical details and considerations.

Take a deep breath in, count 1... 2... 3... and breathe out. You are now centered. Don't hold back. Give it your all.