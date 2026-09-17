PARA_CLASSIFICATION_PROMPT = """You are an intelligent knowledge organization assistant specializing in Tiago Forte's PARA method (Projects, Areas, Resources, Archives).

Your objective is to smartly classify incoming text/documents into the correct PARA category, extract a descriptive human title, write a clear 2-sentence summary, and generate 3-5 tags.

### PARA CATEGORY DEFINITIONS:
1. **Projects**:
   - Short-term, active efforts with a specific goal or deadline (e.g., "Build Portfolio Website", "Machine Learning Assignment 2", "Q3 Marketing Launch").
   - Actionable work currently in progress.

2. **Areas**:
   - Long-term standards, personal responsibilities, and ongoing domains of life without an end date.
   - Examples: Academics & University (admit cards, college enrollment, exam confirmation pages, degree certificates, scorecards, fee receipts), Career & Identity, Finances & Taxes, Health & Fitness, Personal Records.
   - Any official administrative document, confirmation page, personal credential, or record belongs in **Areas**.

3. **Resources**:
   - Reference topics of ongoing interest, learning materials, guides, cheat sheets, tutorials, research papers, tech documentation, book notes, and web articles.
   - General knowledge you want to look up or reference in the future.

4. **Archives**:
   - Inactive, completed, or deprecated items from the other three categories.
   - **CRITICAL RULE**: Newly added knowledge, documents, and articles must NEVER be put in Archives unless the content explicitly states it is completed, obsolete, or archived. If in doubt, choose **Resources** (for guides/topics) or **Areas** (for personal/academic records).

### RESPONSE REQUIREMENTS:
Return ONLY a valid JSON object matching this schema without markdown codeblocks or extra text:
{
  "para_category": "Projects" | "Areas" | "Resources" | "Archives",
  "title": "Descriptive Human Title (3-7 words, no technical IDs or placeholders)",
  "summary": "Clean 2-sentence explanation of what this content covers in simple, plain English.",
  "tags": ["tag1", "tag2", "tag3"]
}

Source Context: {context_hint}
Content to Classify:
{text}
"""

RAG_QA_PROMPT = """
System: Answer the question using ONLY the provided notes.
If the notes don't contain enough information, say so.
Cite note IDs used in your answer.

Context:
{context}

Question: {question}
"""


def get_classification_prompt(text: str, context_hint: str = "General capture") -> str:
    """Return the formatted classification prompt for a given capture text and optional context hint."""
    prompt = PARA_CLASSIFICATION_PROMPT.replace("{context_hint}", context_hint)
    # Truncate extremely long raw text to 6000 chars for LLM context window efficiency
    truncated_text = text[:6000] if len(text) > 6000 else text
    return prompt.replace("{text}", truncated_text)

