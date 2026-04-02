from groq import Groq
from django.conf import settings
from .single_topic_rag import get_question_for_topic

client = Groq(api_key=settings.GROQ_API_KEY)


def generate_question(role, topics, question_number, mode='random'):
    """
    Generate one technical interview question.
    Supports both RAG-based (single topic) and AI-generated (random topics) questions.
    
    Args:
        role: Job role or topic name
        topics: Topics to cover
        question_number: Question number (1-5)
        mode: 'single' for RAG-based, 'random' for AI-generated
    
    Returns:
        Question string
    """
    
    # For single topic mode, use RAG from question bank
    if mode == 'single' and topics.lower() in ['sql', 'python']:
        try:
            question = get_question_for_topic(topics.lower(), question_number)
            if question:
                return question
            # If RAG fails, fall through to AI generation
            print(f"RAG returned None, using AI fallback for {topics}")
        except Exception as e:
            print(f"RAG error: {e}, using AI fallback")
    
    # For random topics mode or fallback, use AI generation
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