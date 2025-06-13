"""Example prompt templates for document enrichment.

These templates provide starting points that users and agents can customize
for their specific enrichment needs.
"""

# Context generation prompts
CONTEXT_PROMPTS = {
    "technical_summary": """
Document: {content}

Write a brief context (2-3 sentences) explaining:
1. What technical problem this solves
2. When someone would need this information
3. Key technologies or concepts involved
""",
    
    "research_context": """
Document: {content}

Provide context (2-3 sentences) covering:
1. The research question or hypothesis
2. Key findings or contributions
3. Relevance to the field
""",
    
    "business_context": """
Document: {content}

Create a business context (2-3 sentences) explaining:
1. The business problem or opportunity
2. Key stakeholders or impacts
3. Strategic importance
""",
    
    "tutorial_context": """
Document: {content}

Write a learning context (2-3 sentences) describing:
1. What skills or knowledge this teaches
2. Prerequisites or target audience
3. Practical applications
""",
}

# Tag extraction prompts
TAG_PROMPTS = {
    "technical_tags": """
Document: {content}

Extract 3-7 tags covering:
- Programming languages mentioned
- Frameworks and libraries
- Technical concepts
- Problem domains

Return as comma-separated list:
""",
    
    "topic_tags": """
Document: {content}

Generate 5-10 topical tags that capture:
- Main subjects discussed
- Key themes
- Domain areas
- Relevant categories

Return as comma-separated list:
""",
    
    "skill_tags": """
Document: {content}

Identify 3-5 tags for:
- Skills taught or required
- Competency levels (beginner, intermediate, advanced)
- Learning outcomes
- Application areas

Return as comma-separated list:
""",
}

# Metadata extraction prompts
METADATA_PROMPTS = {
    "code_metadata": """
Analyze this code and extract:
- Primary programming language
- Main purpose or functionality
- Key dependencies or imports
- Complexity level (1-5)
- Whether it includes tests (yes/no)

Document: {content}

Return as JSON:
""",
    
    "research_metadata": """
Extract from this research document:
- Research type (empirical, theoretical, review)
- Methodology used
- Sample size (if applicable)
- Key findings (list of 2-3)
- Future work mentioned

Document: {content}

Return as JSON:
""",
    
    "meeting_metadata": """
From this meeting document, extract:
- Meeting date
- Participants (list)
- Key decisions (list)
- Action items (list with assignees)
- Next steps

Document: {content}

Return as JSON:
""",
    
    "api_metadata": """
For this API documentation, extract:
- API version
- Base endpoint
- Authentication method
- Main resources (list)
- Rate limits (if mentioned)

Document: {content}

Return as JSON:
""",
}

# Relationship discovery prompts
RELATIONSHIP_PROMPTS = {
    "code_relationships": """
Source code file:
Title: {source_title}
Content: {source_content}

Other files in project:
{candidates}

Identify relationships:
- imports/depends_on: Files this code imports or depends on
- imported_by/used_by: Files that might use this code
- implements: Interfaces or protocols implemented
- extends: Classes or modules extended
- tests/tested_by: Test relationships

Return as JSON array with relationship type and explanation.
""",
    
    "document_citations": """
Source document:
Title: {source_title}
Content excerpt: {source_content}

Reference candidates:
{candidates}

Find citation relationships:
- cites: Documents explicitly referenced
- cited_by: Documents that might reference this
- extends: Builds upon ideas from
- contradicts: Presents opposing views
- supports: Provides supporting evidence

Return as JSON array with relationship type and brief explanation.
""",
    
    "topic_relationships": """
Document:
Title: {source_title}
Summary: {source_content}

Related documents:
{candidates}

Identify topical relationships:
- prerequisite: Should be read before this
- follow_up: Natural next reading
- alternative: Covers same topic differently
- deep_dive: More detailed on specific aspect
- overview: Higher-level view of same topic

Return as JSON array with relationship type and connection explanation.
""",
}

# Purpose-specific enrichment prompts
PURPOSE_PROMPTS = {
    "rag_optimization": """
Prepare this document for a RAG (Retrieval-Augmented Generation) system.

Document: {content}

Provide:
1. CONTEXT: 2-3 sentences on what questions this document can answer
2. TAGS: 5-7 topical tags for retrieval
3. METADATA: JSON with:
   - document_type (reference, tutorial, example, etc.)
   - complexity_level (1-5)
   - key_concepts (list)
   - use_cases (list)
""",
    
    "learning_path": """
Enrich this document for a learning management system.

Document: {content}

Extract:
1. CONTEXT: Learning objectives and outcomes
2. TAGS: Skills and topics covered
3. METADATA: JSON with:
   - difficulty_level (beginner/intermediate/advanced)
   - prerequisites (list)
   - estimated_time (in minutes)
   - learning_outcomes (list)
   - practice_exercises (yes/no)
""",
    
    "knowledge_graph": """
Prepare document for knowledge graph construction.

Document: {content}

Identify:
1. CONTEXT: Core concept and its significance
2. TAGS: Entity types and categories
3. METADATA: JSON with:
   - main_entities (list with types)
   - relationships (list of entity-relation-entity)
   - properties (key attributes)
   - domain (field or area)
""",
    
    "compliance_review": """
Analyze document for compliance and governance.

Document: {content}

Assess:
1. CONTEXT: Compliance relevance and requirements
2. TAGS: Regulations, standards, or policies mentioned
3. METADATA: JSON with:
   - compliance_areas (list)
   - risk_level (low/medium/high)
   - sensitive_data (yes/no)
   - retention_period (if mentioned)
   - approval_required (yes/no)
""",
}

# Batch enrichment prompts
BATCH_PROMPTS = {
    "collection_summary": """
You are analyzing a collection of related documents.

Documents in collection:
{batch_summaries}

For the current document:
Title: {title}
Content: {content}

Provide:
1. CONTEXT: How this document fits within the collection
2. RELATIONSHIPS: Which other documents it relates to and how
3. POSITION: Its logical position or role in the collection
""",
    
    "cross_reference": """
Analyzing document set for cross-references.

All documents:
{batch_summaries}

Current document:
{content}

Find:
1. Direct references to other documents
2. Implicit connections through shared concepts
3. Complementary or contrasting viewpoints

Return as JSON with relationship details.
""",
}


def get_prompt_template(category: str, template_name: str) -> str:
    """Get a specific prompt template.
    
    Args:
        category: Category of prompt (context, tags, metadata, etc.)
        template_name: Name of the template
        
    Returns:
        Prompt template string
        
    Raises:
        KeyError: If category or template not found
    """
    categories = {
        "context": CONTEXT_PROMPTS,
        "tags": TAG_PROMPTS,
        "metadata": METADATA_PROMPTS,
        "relationships": RELATIONSHIP_PROMPTS,
        "purpose": PURPOSE_PROMPTS,
        "batch": BATCH_PROMPTS,
    }
    
    if category not in categories:
        raise KeyError(f"Unknown category: {category}")
    
    prompts = categories[category]
    if template_name not in prompts:
        raise KeyError(f"Unknown template '{template_name}' in category '{category}'")
    
    return prompts[template_name]


def list_available_prompts() -> dict[str, list[str]]:
    """List all available prompt templates by category."""
    return {
        "context": list(CONTEXT_PROMPTS.keys()),
        "tags": list(TAG_PROMPTS.keys()),
        "metadata": list(METADATA_PROMPTS.keys()),
        "relationships": list(RELATIONSHIP_PROMPTS.keys()),
        "purpose": list(PURPOSE_PROMPTS.keys()),
        "batch": list(BATCH_PROMPTS.keys()),
    }


# Convenience function for custom prompts
def build_enhancement_prompt(
    task: str,
    fields: list[str],
    context: str = "",
    examples: str = ""
) -> str:
    """Build a custom enrichment prompt.
    
    Args:
        task: Description of the enrichment task
        fields: List of fields to extract
        context: Additional context about the use case
        examples: Example outputs (optional)
        
    Returns:
        Formatted prompt string
    """
    prompt = f"{task}\n\n"
    
    if context:
        prompt += f"Context: {context}\n\n"
    
    prompt += "Extract/generate the following:\n"
    for field in fields:
        prompt += f"- {field}\n"
    
    if examples:
        prompt += f"\nExamples:\n{examples}\n"
    
    prompt += "\nDocument: {content}\n\nOutput:"
    
    return prompt