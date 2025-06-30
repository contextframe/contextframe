Extract deep knowledge about: $ARGUMENTS

<ultrathink>
Investigative journalism mode. Uncover the complete story - WHY it exists, HOW it evolved, WHAT it teaches.
</ultrathink>

<megaexpertise type="knowledge-engineer">
The assistant should dig into history, design decisions, trade-offs, document the undocumented, and capture tribal knowledge.
</megaexpertise>

<context>
Knowledge extraction for: $ARGUMENTS
Create organizational memory that makes future work easier
</context>

<requirements>
- Code archaeology (git history, evolution, major changes)
- Design rationale (why this approach, alternatives considered)
- Dependency mapping (uses, used by, breaking impacts)
- Usage patterns (common, advanced, mistakes to avoid)
- Tribal knowledge (gotchas, tricks, workarounds)
- Performance characteristics
- Future roadmap ideas
</requirements>

<actions parallel="true">
1. git log --follow -- $ARGUMENTS && git blame $ARGUMENTS
2. rg -l "$ARGUMENTS" → find all usages
3. rg -B2 -A2 "$ARGUMENTS" → understand contexts
4. Ask as if interviewing creator: Why created? Alternatives? Do differently? Most important? Breaks often? Bottlenecks?
5. Document undocumented: deployment gotchas, config secrets, debugging tricks, tuning, known issues
6. Create `.claude/knowledge/$ARGUMENTS/` structure:
   - Executive Summary
   - Core Concepts  
   - Architecture & Design
   - Usage Guide (basic, advanced, troubleshooting)
   - Implementation Details
   - Performance Characteristics
   - Evolution History
   - Lessons Learned
7. Generate one-page quick reference
8. Create FAQ from issues and comments
</actions>

The assistant should create time capsule for future developers so they understand the full story - not just WHAT but WHY and HOW to work with it effectively.

Take a deep breath in, count 1... 2... 3... and breathe out. The assistant is now centered and should not hold back but give it their all.
