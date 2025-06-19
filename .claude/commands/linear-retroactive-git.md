Analyze git working state and create comprehensive Linear issues using the Linear MCP

<ultrathink>
This command will analyze git changes and use the Linear MCP to create rich, detailed issues in Linear with comprehensive documentation and organization.
</ultrathink>

<megaexpertise type="project-management-automation-expert">
Leverage Linear's API through MCP to create well-structured issues with detailed scope, technical documentation, and proper metadata based on git changes.
</megaexpertise>

<context>
Automate the process of converting git working state into comprehensive Linear issues using the Linear MCP
</context>

<requirements>
- Analyze git status and changes in detail
- Create comprehensive issue descriptions with full scope
- Use Linear MCP to create richly documented issues
- Organize issues with proper sections and formatting
- Apply appropriate labels and metadata
- Link to existing issues when relevant
- Include detailed technical context
- Create GitHub pull requests for each branch
</requirements>

<actions>
1. **Analyze Git State**:
   ```bash
   # Get current changes
   git status --porcelain
   git diff --stat
   git diff --name-status
   ```

2. **Check Linear Context**:
   - Use `mcp__linear__get_team` to get team info
   - Use `mcp__linear__list_issue_statuses` to get available statuses
   - Use `mcp__linear__list_issue_labels` to get available labels
   - Use `mcp__linear__list_projects` to identify relevant project

3. **Search for Related Existing Issues and Projects**:
   - Use `mcp__linear__list_projects` to find active projects that could organize this work
   - Check for projects with status != "completed" or "cancelled"
   - Use `mcp__linear__list_issues` to find related open issues
   - Check issue titles and descriptions for relevance
   - Determine if changes should be attached to existing issues or projects

4. **Categorize Changes**:
   - Group by component/module
   - Identify change types and map to Linear labels:
     - Feature (new functionality)
     - Bug (fixes)
     - Refactor (code improvements)
     - Documentation (docs updates)
     - Improvement (enhancements)
     - Testing (test additions/updates)
     - Technical Debt (cleanup)
     - Performance (optimizations)
     - Security (security improvements)
     - Maintenance (dependency updates, etc.)

5. **Create Project and Issue Structure**:

   For major groups of related changes:
   
   a) **Find or Create a Project to organize related work**:
      ```javascript
      // First, check for existing applicable projects
      const existingProjects = await mcp__linear__list_projects({ 
        teamId: team.id,
        includeArchived: false 
      });
      
      // Look for active projects that match our work
      let project = existingProjects.find(p => {
        const isActive = !p.completedAt && !p.canceledAt && !p.archivedAt;
        const isRelevant = p.name.includes("Refactor") || 
                          p.name.includes("AI Agent") ||
                          p.description?.includes("agent") ||
                          p.description?.includes("refactor");
        return isActive && isRelevant;
      });
      
      // Only create new project if no suitable one exists
      if (!project) {
        project = await mcp__linear__create_project({
          name: "Refactor: AI Agent Architecture",
          teamId: team.id,
          summary: "Consolidate AI agent system and remove redundant code",
          description: `## Overview
          Major refactoring effort to improve the AI agent system by removing redundant code and implementing cleaner patterns.
        
        ## Scope
        - Remove duplicate response models across all agents
        - Consolidate tool imports
        - Fix import issues and circular dependencies
        - Implement proper factory pattern
        - Clean up unused evaluation files
        
        ## Affected Components
        - Healthcare Agent
        - Education Agent  
        - Exa Agent
        - Agent Registry and Factory
        - Test Suite
        
        ## Technical Approach
        1. Audit current agent implementations
        2. Remove duplicate files
        3. Update imports to use centralized tools
        4. Ensure all tests pass
          5. Update documentation`,
          targetDate: "2025-07-01"
        });
      } else {
        console.log(`Using existing project: ${project.name} (${project.id})`);
      }
      ```
      
      **When to create new projects vs use existing:**
      - Use existing if: Similar scope, active status, room for more issues
      - Create new if: Different scope, existing is too large, need separate tracking
      - Always prefer reusing active projects to avoid project sprawl

   b) **Create focused issues within the project**:
      ```javascript
      // Issue 1: Remove duplicate response models
      const issue1 = await mcp__linear__create_issue({
        title: "Remove duplicate response models from agents",
        description: `## Context
        Part of the AI Agent Architecture refactoring project.
        
        ## Scope
        Remove redundant response model files and consolidate definitions.
        
        ## Technical Details
        - Delete: app/services/ai/agents/healthcare_agent/response_models.py
        - Delete: app/services/ai/agents/education_agent/response_models.py  
        - Delete: app/services/ai/agents/exa_agent/response_models.py
        - Move response model definitions directly into agent files
        
        ## Implementation
        1. Copy response model classes to respective agent files
        2. Update imports in agent files
        3. Delete redundant response_models.py files
        4. Run tests to ensure nothing breaks
        
        ## Acceptance Criteria
        - [ ] All response_models.py files removed
        - [ ] Response models defined in agent files
        - [ ] All imports updated
        - [ ] All tests pass`,
        projectId: project.id,
        labelIds: [refactor_label_id, technical_debt_label_id],
        estimate: 2
      });

      // Issue 2: Consolidate tool imports
      const issue2 = await mcp__linear__create_issue({
        title: "Consolidate tool imports across all agents",
        description: `## Context
        Part of the AI Agent Architecture refactoring project.
        
        ## Scope
        Update all agents to use centralized tools from app/services/ai/tools/
        
        ## Files to update:
        - app/services/ai/agents/healthcare_agent/agent.py
        - app/services/ai/agents/education_agent/agent.py
        - app/services/ai/agents/exa_agent/agent.py
        
        ## Changes needed:
        FROM: from .tools import sql_query, vector_search
        TO: from app.services.ai.tools.sql_query import sql_query
            from app.services.ai.tools.vector_search import vector_search`,
        projectId: project.id,
        labelIds: [refactor_label_id, improvement_label_id],
        estimate: 1
      });
      ```

6. **Link Issues to Git Context**:
   - Add current branch name to issue description
   - Include list of affected files
   - Add commit message suggestions

7. **Update Existing Issues** (if applicable):
   - Use `mcp__linear__update_issue` to add progress notes
   - Use `mcp__linear__create_comment` to add implementation details
   - Update status if work is complete

8. **Generate Summary Report**:
   ```markdown
   # Linear Project and Issues Created
   
   ## Project Created:
   - Refactor: AI Agent Architecture
     - URL: https://linear.app/greyhaven/project/refactor-ai-agent-architecture
     - Target Date: 2025-07-01
     - Issues: 4
   
   ## Issues Created (within project):
   - CVIREC-20: Remove duplicate response models from agents
     - Labels: Refactor, Technical Debt
     - Branch: jayscambler/cvirec-20-remove-duplicate-response-models
     - PR: #21
   
   - CVIREC-21: Consolidate tool imports across all agents
     - Labels: Refactor, Improvement
     - Branch: jayscambler/cvirec-21-consolidate-tool-imports
     - PR: #22
   
   - CVIREC-22: Update database models and type hints
     - Labels: Improvement, Technical Debt
     - Branch: jayscambler/cvirec-22-update-database-models
     - PR: #23
   
   - CVIREC-23: Clean up unused evaluation files
     - Labels: Technical Debt
     - Branch: jayscambler/cvirec-23-clean-up-evaluation-files
     - PR: #24
   
   ## Pull Requests:
   - All PRs linked to project issues
   - Ready for review
   - CI/CD status visible in Linear
   
   ## Project Progress:
   - Total Issues: 4
   - In Progress: 4
   - Completed: 0
   - Estimated Points: 8
   
   ## Next Steps:
   1. Review and approve PRs
   2. Merge when tests pass
   3. Update Linear issue status
   4. Track progress in project view
   ```

</actions>

## Workflow Example

```javascript
// 1. Get team info
const team = await mcp__linear__get_team({ query: "CVI Rec Sys" });

// 2. Get available labels
const labels = await mcp__linear__list_issue_labels({ teamId: team.id });
const refactorLabel = labels.find(l => l.name === "Refactor");
const improvementLabel = labels.find(l => l.name === "Improvement");

// 3. Check for existing projects
const existingProjects = await mcp__linear__list_projects({ 
  teamId: team.id,
  includeArchived: false 
});

// Look for active, relevant project
let project = existingProjects.find(p => {
  const isActive = !p.completedAt && !p.canceledAt;
  const isRelevant = p.name.includes("AI Agent") || 
                    p.name.includes("Refactor");
  return isActive && isRelevant;
});

// 4. Only create new project if needed
if (!project) {
  project = await mcp__linear__create_project({
    name: "Refactor: AI Agent Architecture",
    teamId: team.id,
    summary: "Consolidate AI agent system and remove redundant code",
    description: "Major refactoring effort...",
    targetDate: "2025-07-01"
  });
  console.log("Created new project:", project.name);
} else {
  console.log("Using existing project:", project.name);
  // Optionally update project description to include new work
  await mcp__linear__update_project({
    id: project.id,
    description: project.description + "\n\n## Additional Work\n- Git changes from " + new Date().toISOString()
  });
}

// 5. Create issues within the project
const issues = [];

// First issue
issues.push(await mcp__linear__create_issue({
  title: "Remove duplicate response models from agents",
  description: "Remove redundant response model files...",
  projectId: project.id,
  teamId: team.id,
  labelIds: [refactorLabel.id],
  priority: 3,
  estimate: 2
}));

// Second issue  
issues.push(await mcp__linear__create_issue({
  title: "Consolidate tool imports across all agents",
  description: "Update all agents to use centralized tools...",
  projectId: project.id,
  teamId: team.id,
  labelIds: [refactorLabel.id, improvementLabel.id],
  priority: 3,
  estimate: 1
}));

// 6. Update project with issue links
await mcp__linear__update_project({
  id: project.id,
  description: project.description + `\n\n## Issues\n${issues.map(i => `- ${i.identifier}: ${i.title}`).join('\n')}`
});
```

## Integration Points

1. **Branch Naming**: Use Linear's branch format
   ```javascript
   const branchName = await mcp__linear__get_issue_git_branch_name({ 
     issueId: parentIssue.id 
   });
   ```

2. **Status Updates**: Move issues through workflow
   ```javascript
   await mcp__linear__update_issue({
     issueId: subIssue1.id,
     stateId: inProgressState.id
   });
   ```

3. **Comments**: Add implementation notes
   ```javascript
   await mcp__linear__create_comment({
     issueId: parentIssue.id,
     body: "Started implementation. See branch: " + branchName
   });
   ```

## Retroactive Branch Creation and PR Workflow

When dealing with changes already in the working state:

1. **Create Comprehensive Backup**:
   ```bash
   # Save current state
   git add -A
   git stash save "Full working state backup for Linear issues"
   ```

2. **For Each Issue Created**:
   ```bash
   # Get branch name from Linear
   branchName = await mcp__linear__get_issue_git_branch_name({ 
     issueId: issue.id 
   });
   
   # Create and checkout new branch from main
   git checkout main
   git checkout -b ${branchName}
   
   # Apply only relevant changes for this issue
   git checkout stash@{0} -- ${files_for_this_issue}
   
   # Commit with Linear issue reference
   git add ${files_for_this_issue}
   git commit -m "${issueIdentifier}: ${issueTitle}
   
   ${issueDescription}
   
   Resolves: ${issueUrl}"
   
   # Push branch
   git push -u origin ${branchName}
   
   # Create Pull Request
   gh pr create \
     --title "${issueIdentifier}: ${issueTitle}" \
     --body "## Summary
   ${issueSummary}
   
   ## Linear Issue
   ${issueUrl}
   
   ## Changes
   ${changesList}
   
   ## Testing
   - [ ] All tests pass
   - [ ] Manual testing completed
   - [ ] No regressions identified" \
     --base main \
     --head ${branchName} \
     --assignee @me
   
   # Return to main for next issue
   git checkout main
   ```

3. **Selective File Application**:
   - Group files by issue/component
   - Use `git checkout stash@{0} -- file1 file2` for selective restoration
   - Maintain clean separation between issues

4. **Branch Strategy**:
   - Each issue gets its own branch
   - Project can track overall progress across branches
   - Use Linear's branch naming convention for automatic linking
   - Branches automatically link to Linear issues via naming

5. **Commit Messages**:
   - Include Linear issue identifier (e.g., CVIREC-21)
   - Reference project name in commit body if relevant
   - Link to Linear issue URL for context
   - Keep messages clear and descriptive

Remember to:

- **Check for existing projects first** - avoid creating duplicate projects
- Use existing active projects when they match your work scope
- Check for duplicate issues before creating new ones
- Use consistent labeling from available Linear labels
- Create comprehensive issue descriptions with full technical context
- Include enough context for other developers
- Update issue status as work progresses
- Create separate branches for each issue when dealing with retroactive changes
- Use selective git operations to maintain clean separation
- Always create PRs that link back to Linear issues
- Use Linear's branch naming convention for automatic linking

**Project Management Best Practices:**
- One project per major feature/refactor effort
- Reuse projects for related work over time
- Close projects when all issues are complete
- Use project descriptions to maintain context
- Update project target dates as needed
