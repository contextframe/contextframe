
Run pre-commit workflow and systematically fix all errors found

<ultrathink>
This is a development workflow optimization task. Need to create a systematic approach to:
1. Run pre-commit checks
2. Categorize errors by type
3. Fix them in the most efficient order
4. Verify fixes don't break anything
</ultrathink>

<megaexpertise type="code-quality-specialist">
Leverage understanding of common linting patterns, type checking issues, and formatting standards to efficiently resolve all pre-commit failures.
</megaexpertise>

<context>
Running pre-commit checks to ensure code quality before commits
Need to fix all issues systematically and efficiently
</context>

<requirements>
- Run pre-commit hooks and capture all output
- Categorize errors by type and severity
- Fix issues in optimal order (formatting → imports → linting → type checking)
- Verify each fix doesn't introduce new issues
- Provide clear summary of all changes made
</requirements>

<actions>
0. **IMPORTANT**: First activate the virtual environment:
   - Run `source .venv/bin/activate`
   - This is required for all Python-related commands below

1. Check the current git status to understand what files we're checking:
   - Run `git status` to see modified files
   - Note which files will be checked by pre-commit

2. Run initial pre-commit check to see all issues:
   - Execute `task pre-commit` or `pre-commit run --all-files`
   - Capture and analyze the output

3. Fix issues in this order for efficiency:
   a) **Auto-fixable formatting issues** (these are quick wins):
      - Run `task format` to fix formatting with ruff
      - Run `task lint` to fix auto-fixable linting issues
   
   b) **Import issues**:
      - Ruff with isort will fix import ordering
      - Remove unused imports if any remain
   
   c) **JSON/YAML formatting**:
      - Pre-commit will auto-format JSON files
      - Fix any YAML syntax errors
   
   d) **File issues**:
      - Fix missing newlines at end of files
      - Fix mixed line endings
      - Remove any debug statements
   
   e) **Type checking errors** (if any):
      - Fix MyPy errors by adding type annotations
      - Handle missing imports for type checking

4. After each category of fixes, run pre-commit again to verify:
   - `pre-commit run --all-files`
   - This ensures we haven't introduced new issues

5. Final verification:
   - Run all tests: `task test`
   - Ensure no functionality was broken by the fixes

6. Provide summary of all changes made

7. If any errors persist that can't be auto-fixed:
   - Provide detailed explanation of each error
   - Show exact code locations and suggested fixes
   - Explain why manual intervention might be needed
</actions>

## Error Pattern Reference

### Common Ruff Errors and Fixes:

- **F401 (unused import)**: Remove the import or add `# noqa: F401` if needed
- **E501 (line too long)**: Break long lines, but this is ignored in config
- **I001 (import order)**: Ruff will auto-fix with `--fix`
- **UP (pyupgrade)**: Modernizes Python syntax automatically

### Common MyPy Errors and Fixes:

- **Missing imports**: Add type stubs or use `# type: ignore[import]`
- **Untyped functions**: Add type hints or configure MyPy to be less strict
- **Type mismatches**: Fix the actual type issues in code

### Pre-commit Hook Fixes:

- **Large files**: Remove or git-lfs track files over 1MB
- **Merge conflicts**: Resolve conflict markers
- **Private keys**: Remove any detected private keys immediately
- **Debug statements**: Remove print(), breakpoint(), etc.

Remember: The goal is clean, consistent code that passes all checks. Fix systematically, verify frequently, and ensure the codebase remains functional throughout the process.