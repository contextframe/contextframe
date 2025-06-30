Debug systematically: $ARGUMENTS

<ultrathink>
Think harder. Dig deeper. Find root cause, not symptoms.
</ultrathink>

<megaexpertise type="debugging-specialist">
The assistant should use scientific method, generate hypotheses, design tests, prove/disprove, and extract maximum learning.
</megaexpertise>

<context>
Debugging issue: $ARGUMENTS
Need root cause analysis and comprehensive fix
</context>

<requirements>
- Minimal reproduction case
- Complete error capture (messages, logs, stack traces, environment)
- Multiple hypotheses (most likely, most dangerous, most subtle)
- Scientific testing approach
- Root cause fix (not symptom patch)
- Regression prevention
- Knowledge capture
</requirements>

<actions>
1. Create Linear tracking:
   - For simple bugs: mcp_linear.create_issue(title="[Bug] $ARGUMENTS", description="Systematic debugging with RCA")
   - For complex bugs: Create project with issues for investigation, fix, tests, and prevention
2. Reproduce → document exact steps, intermittency patterns
3. Generate ranked hypotheses → think harder about causes
4. Design specific tests for each hypothesis
5. Add targeted logging: logger.debug(f"State: {state}, Inputs: {inputs}, Conditions: {conditions}")
6. Fix root cause → handle all discovered edge cases
7. Write failing test → add integration test → document pattern
8. Create `.claude/debugging/[issue-type].md` with full learnings
9. If using project: Update all related issues with findings
</actions>

This bug teaches us about our system. The assistant should extract maximum value while fixing thoroughly and think deeply - what is this bug really telling us?

Take a deep breath in, count 1... 2... 3... and breathe out. The assistant is now centered and should not hold back but give it their all.
