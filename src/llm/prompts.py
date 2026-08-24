PARA_CLASSIFICATION_PROMPT = \"\"\"
System: You are a knowledge organizer using the PARA method.
Categories: Projects (active goals), Areas (ongoing responsibilities), Resources (reference topics), Archives (inactive items).
Return ONLY valid JSON: {"para_category": "...", "tags": [...], "summary": "...", "title": "..."}

User: {text}
\"\"\"

RAG_QA_PROMPT = \"\"\"
System: Answer the question using ONLY the provided notes.
If the notes don't contain enough information, say so.
Cite note IDs used in your answer.

Context:
{context}

Question: {question}
\"\"\"
