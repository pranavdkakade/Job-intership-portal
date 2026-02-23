from groq import Groq
from django.conf import settings
import json

client = Groq(api_key=settings.GROQ_API_KEY)


def evaluate_answer(question, user_answer):
    prompt = f"""
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

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0,
            messages=[
                {"role": "system", "content": "You are a strict technical interviewer."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content.strip()

        # Extract JSON safely
        start = content.find("{")
        end = content.rfind("}") + 1

        if start == -1 or end == -1:
            return {"score": 0, "feedback": "Invalid evaluation format returned."}

        json_string = content[start:end]

        result = json.loads(json_string)

        # Ensure score is integer
        score = int(result.get("score", 0))

        # Clamp score between 0 and 10
        score = max(0, min(score, 10))

        feedback = result.get("feedback", "No feedback provided.")

        return {
            "score": score,
            "feedback": feedback
        }

    except Exception as e:
        return {
            "score": 0,
            "feedback": f"Evaluation error: {str(e)}"
        }