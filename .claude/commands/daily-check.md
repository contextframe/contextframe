Perform comprehensive daily development check: $ARGUMENTS

<ultrathink>
What needs attention? What's blocked? What moves the project forward today?
</ultrathink>

<megaexpertise type="project-manager">
Analyze Linear issues, git state, code quality. Create focused action plan optimizing for flow and impact.
</megaexpertise>

<context>
Daily standup replacement - comprehensive development status and prioritization
Need clear picture of work state and optimal task order
</context>

<requirements>
- Linear status (in progress, todo, blocked, in review)
- Git repository state (branch, changes, pending PRs)
- Code quality indicators (tests, linting, coverage)
- Priority matrix (urgent/important, quick wins)
- Health indicators (tech debt, blockers, days since deploy)
</requirements>

<actions parallel="true">
1. mcp_linear.list_my_issues() → categorize by status
2. git status && git diff --stat && git log --oneline -10
3. gh pr list --author @me
4. pytest -x && ruff check --select E,F
5. Generate priority matrix: 🔴 Urgent (blocked PRs, critical bugs) 🟡 Important (features, reviews) 🟢 Quick wins
6. Create focused action items with specific Linear issue numbers
7. Identify blockers, risks, coordination needs
8. Generate end-of-day checklist
</actions>

Cut through noise. Highlight what truly needs attention. Make today productive and move the project forward meaningfully.

Take a deep breath in, count 1... 2... 3... and breathe out. You are now centered. Don't hold back. Give it your all.