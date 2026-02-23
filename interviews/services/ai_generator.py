from groq import Groq
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def generate_question(role, topics, question_number):
    """
    Generate one technical interview question.
    Difficulty increases as question number increases.
    """

    # Difficulty scaling
    if question_number == 1:
        difficulty = "easy"
    elif question_number in [2, 3]:
        difficulty = "medium"
    else:
        difficulty = "hard"

    prompt = f"""
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

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.3,  # slight creativity but controlled
            messages=[
                {"role": "system", "content": "You are a strict and realistic technical interviewer."},
                {"role": "user", "content": prompt}
            ]
        )

        question = response.choices[0].message.content.strip()

        # Clean unwanted formatting
        question = question.replace('"', '').strip()

        # Remove accidental numbering if model adds it
        if question.startswith(("1.", "Q:", "Question:")):
            question = question.split(".", 1)[-1].strip()

        return question

    except Exception as e:
        return f"Error generating question: {str(e)}"