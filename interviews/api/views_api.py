 # Handles AJAX calls

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from interviews.models import InterviewSession, InterviewQuestion
from interviews.services.ai_generator import generate_question
from interviews.services.ai_evaluator import evaluate_answer

from django.contrib.auth.models import User

@csrf_exempt
def chat_interview(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message")
        # user = request.user
        user = User.objects.first()

        session, created = InterviewSession.objects.get_or_create(
            user=user,
            is_completed=False
        )

        # START
        if session.stage == "waiting_for_start":
            if message.lower() == "go":
                session.stage = "waiting_for_role"
                session.save()
                return JsonResponse({"reply": "What job profile?"})
            return JsonResponse({"reply": "Type 'go' to start interview."})

        # ROLE
        if session.stage == "waiting_for_role":
            session.role = message
            session.stage = "waiting_for_topics"
            session.save()
            return JsonResponse({"reply": "Which topics?"})

        # TOPICS
        if session.stage == "waiting_for_topics":
            session.topics = message
            session.stage = "interview_started"
            session.current_question_number = 1
            session.save()

            try:
                question = generate_question(
                    session.role,
                    session.topics,
                    1
                )

                InterviewQuestion.objects.create(
                    session=session,
                    question_text=question
                )

                session.stage = "waiting_for_answer"
                session.save()

                return JsonResponse({"reply": f"Question 1: {question}"})
            
            except Exception as e:
                # Reset session on error
                session.stage = "waiting_for_topics"
                session.save()
                return JsonResponse({"reply": f"Error generating question: {str(e)}. Please try again."})

        # ANSWER
        if session.stage == "waiting_for_answer":
            question_obj = session.questions.last()
            question_obj.user_answer = message

            try:
                result = evaluate_answer(
                    question_obj.question_text,
                    message
                )

                question_obj.score = result["score"]
                question_obj.feedback = result["feedback"]
                question_obj.save()

                session.total_score += result["score"]

                # If 5 questions done
                if session.current_question_number == 5:
                    final_score = round(session.total_score / 5, 2)
                    session.stage = "completed"
                    session.is_completed = True
                    session.save()

                    return JsonResponse({
                        "reply": f"""
Score: {result['score']}/10
Feedback: {result['feedback']}

Interview Completed ✅
Final Score: {final_score}/10
"""
                    })

                # Else next question
                session.current_question_number += 1
                next_q_number = session.current_question_number
                session.save()

                next_question = generate_question(
                    session.role,
                    session.topics,
                    next_q_number
                )

                InterviewQuestion.objects.create(
                    session=session,
                    question_text=next_question
                )

                return JsonResponse({
                    "reply": f"""
Score: {result['score']}/10
Feedback: {result['feedback']}

Question {next_q_number}: {next_question}
"""
                })
            
            except Exception as e:
                return JsonResponse({"reply": f"Error processing answer: {str(e)}. Please try again."})

    return JsonResponse({"reply": "Invalid request"})