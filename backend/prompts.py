DECOMPOSE_PROMPT = """You are a research assistant. Your job is to break down a complex question into 3 simpler sub-questions that together will answer the original question.

Original question: {question}

Return exactly 3 sub-questions as a numbered list, nothing else. Example format:
1. First sub-question
2. Second sub-question
3. Third sub-question"""


SYNTHESIZE_PROMPT = """You are a research assistant. Using the retrieved information below, write a comprehensive answer to the original question.

Original question: {question}

Retrieved information:
{context}

Instructions:
- Answer directly and clearly
- Cite your sources using [Source X] notation
- Be specific and use facts from the retrieved information
- Keep your answer under 300 words

Answer:"""