from fastapi import APIRouter, HTTPException, Depends
from pymongo import MongoClient
import random
from ..schemas import Question, QuizAttempt

router = APIRouter()

@router.post("/start-quiz")
async def start_quiz(course_id: str, user_id: str, db: MongoClient = Depends(get_db)):
    """Start a new adaptive quiz session"""
    # Fetch questions for this course
    questions = list(db.questions.find({"course_id": course_id}))
    
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this course")
    
    # Create quiz attempt
    attempt = {
        "user_id": user_id,
        "course_id": course_id,
        "current_ability": 0.5,
        "questions_answered": [],
        "started_at": datetime.now().isoformat()
    }
    
    result = db.quiz_attempts.insert_one(attempt)
    
    # Select first question (medium difficulty)
    first_question = select_question(questions, target_difficulty=0.5)
    
    return {
        "attempt_id": str(result.inserted_id),
        "question": first_question,
        "total_questions": len(questions)
    }

@router.post("/answer")
async def answer_question(attempt_id: str, question_id: str, answer: str, db: MongoClient = Depends(get_db)):
    """Process user answer and get next question"""
    # Get attempt
    attempt = db.quiz_attempts.find_one({"_id": ObjectId(attempt_id)})
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    # Get question
    question = db.questions.find_one({"_id": ObjectId(question_id)})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check answer
    is_correct = answer == question["correct_answer"]
    
    # Update ability score (simplified adaptive logic)
    old_ability = attempt["current_ability"]
    performance = 1 if is_correct else 0
    new_ability = old_ability + 0.1 * (performance - old_ability)
    
    # Record answer
    db.quiz_attempts.update_one(
        {"_id": ObjectId(attempt_id)},
        {
            "$push": {
                "questions_answered": {
                    "question_id": question_id,
                    "user_answer": answer,
                    "is_correct": is_correct
                }
            },
            "$set": {"current_ability": new_ability}
        }
    )
    
    # Get next question based on new ability
    all_questions = list(db.questions.find({"course_id": attempt["course_id"]}))
    next_question = select_question(all_questions, target_difficulty=new_ability)
    
    return {
        "is_correct": is_correct,
        "new_ability": new_ability,
        "next_question": next_question
    }

def select_question(questions, target_difficulty):
    """Select question closest to target difficulty level"""
    # Get questions not yet answered in this session
    # For simplicity, this just picks a random question with closest difficulty
    return min(questions, key=lambda q: abs(q["difficulty"] - target_difficulty))