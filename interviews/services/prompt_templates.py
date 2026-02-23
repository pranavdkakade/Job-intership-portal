# Stores structured AI prompts
def question_prompt(role, topics, question_number, difficulty):
    return f"""
You are a professional technical interviewer.

Role: {role}
Topics: {topics}
Question Number: {question_number} out of 5
Difficulty Level: {difficulty}

Instructions:
- Generate ONE clear and practical technical interview question.
- Do NOT include numbering.
- Do NOT include explanation.
- Do NOT include extra text.
- Return only the question sentence.
"""


def evaluation_prompt(question, user_answer):
    return f"""
You are evaluating a technical interview answer.

Question:
{question}

Candidate Answer:
{user_answer}

Instructions:
- Score strictly from 0 to 10.
- Be strict and realistic.
- Do NOT be generous.
- Return ONLY valid JSON.

Return format:
{{
    "score": number_between_0_and_10,
    "feedback": "short technical feedback"
}}
"""