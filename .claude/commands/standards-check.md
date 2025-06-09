Comprehensive standards compliance check: $ARGUMENTS

<ultrathink>
Don't just check - actively fix. Elevate code to excellence.
</ultrathink>

<megaexpertise type="quality-engineer">
Meticulous standards enforcement. Auto-fix everything possible. Make code exemplary.
</megaexpertise>

<context>
Checking standards compliance for: $ARGUMENTS
Need to meet all project standards automatically
</context>

<requirements>
- Code standards (line length, imports, types, docstrings)
- Testing standards (coverage, structure, naming)
- Mirascope/Lilypad patterns
- Pre-commit compliance
- Documentation completeness
- Security and performance
</requirements>

<actions>
1. Code Standards (`.claude/standards/code-standards.md`):
   - Fix line length ≤ 130
   - Organize imports: stdlib → third-party → local
   - Add missing type hints
   - Ensure Google-style docstrings
   - Remove debug statements
   - Fix naming conventions
   
2. Testing Standards (`.claude/standards/testing-standards.md`):
   - Check coverage: 80% overall, 90%+ business logic
   - Generate missing tests
   - Fix test structure and naming
   
3. Framework Patterns:
   - Proper @llm.call, @prompt_template usage
   - Async patterns for LLM calls
   - Response model definitions
   - Error handling with retries
   
4. Auto-fix with tools:
   ```bash
   ruff check --fix && ruff format
   pre-commit run --all-files
   ```
   
5. Documentation: verify all public functions documented
6. Security: no hardcoded secrets, input validation, SQL safety
7. Generate report:
   ```markdown
   ## Compliance Report
   - Score: X/10
   - Auto-fixed: X issues
   - Manual needed: X items
   - [Detailed findings]
   - [Applied fixes]
   - [Remaining actions]
   ```
</actions>

Don't just report issues - fix everything possible automatically. Make this code exemplary. Elevate quality to highest standards.

Take a deep breath in, count 1... 2... 3... and breathe out. You are now centered. Don't hold back. Give it your all.