Generate comprehensive test suite for: $ARGUMENTS

<ultrathink>
Strategic coverage. Focus effort where it matters. Prevent real bugs.
</ultrathink>

<megaexpertise type="qa-engineer">
Apply 80/20 rule. Test critical paths thoroughly, common cases well, edge cases smartly.
</megaexpertise>

<context>
Creating test suite for: $ARGUMENTS
Need meaningful protection against regressions
</context>

<requirements>
- Map all functions, dependencies, critical paths
- Priority 1: Core business logic (50% effort)
- Priority 2: Happy paths (30% effort)  
- Priority 3: Edge cases (20% effort)
- Performance benchmarks for critical operations
- Test utilities (factories, mocks, fixtures)
- 80% overall coverage, 90%+ for business logic
</requirements>

<actions>
1. Analyze code structure → identify test targets
2. Generate test file structure with proper fixtures
3. Write comprehensive happy path tests first
4. Add error handling tests with specific assertions
5. Create parametrized edge case tests
6. Add performance benchmarks: assert benchmark.stats['median'] < 0.1
7. Generate test data factories and mock helpers
8. Run coverage: pytest --cov=$ARGUMENTS --cov-report=term-missing
9. Document test intentions (what, why, failure meaning)
</actions>

Every test should prevent a real bug. Make the test suite a safety net that catches issues before users do. Generate tests that give confidence in deployment.

Take a deep breath in, count 1... 2... 3... and breathe out. You are now centered. Don't hold back. Give it your all.