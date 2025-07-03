Continue testing for the following: $ARGUMENTS

<ultrathink>
Resume testing systematically. Understand coverage gaps. Identify untested scenarios. Ensure comprehensive quality.
</ultrathink>

<megaexpertise type="testing-continuation-specialist">
The assistant should pick up testing where left off, map test coverage, identify gaps, write missing tests, and ensure robust validation.
</megaexpertise>

<context>
Continuing testing for: $ARGUMENTS
Need to assess current test state and complete comprehensive coverage
</context>

<requirements>
- Find associated Linear issue and understand feature scope
- Review existing test coverage
- Identify missing test scenarios
- Write comprehensive tests
- Update Linear with testing progress
</requirements>

<actions>
1. Find Linear issue and context:
   - Check git branch for issue ID: git rev-parse --abbrev-ref HEAD
   - Get issue details: mcp_linear.get_issue(id)
   - Review acceptance criteria for test requirements
   - Check comments for reported bugs or edge cases
   
2. Assess current test coverage:
   - Run existing tests: pytest -v (or project-specific test command)
   - Generate coverage report: pytest --cov=contextframe --cov-report=html
   - Review coverage gaps in key files
   - Check for TODO/FIXME in test files
   
3. Identify missing test scenarios:
   - Unit tests for individual functions/methods
   - Integration tests for feature workflows
   - Edge cases from issue comments or discovered bugs
   - Error handling and validation tests
   - Performance/load tests if applicable
   
4. Write comprehensive tests:
   - Start with failing tests for uncovered scenarios
   - Test happy paths and error conditions
   - Include boundary value tests
   - Add regression tests for any bugs found
   - Document test purpose and expected behavior
   
5. Validate test quality:
   - Ensure tests fail when code is broken
   - Check test isolation (no order dependencies)
   - Verify test data cleanup
   - Run tests multiple times for flakiness
   - Review test readability and maintenance
   
6. Update Linear tracking:
   - Comment with test coverage improvements
   - List any discovered issues or concerns
   - Update issue status if testing complete
   - Create new issues for bugs found during testing
   - Use magic words in commits:
     - "Refs TEAM-123" for test additions
     - "Fixes TEAM-123" if tests complete the issue

7. Generate test summary:
   - Coverage before/after metrics
   - New test scenarios added
   - Any failing tests that need fixes
   - Recommendations for additional testing
</actions>

Quality is ensured through comprehensive testing. The assistant should continue systematically to catch issues before users do.

Take a deep breath in, count 1... 2... 3... and breathe out. The assistant is now centered and should not hold back but give it their all.
