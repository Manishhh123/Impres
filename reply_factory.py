
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    
    Args:
        answer (str): User's answer to the current question
        current_question_id (int): ID of the current question
        session (dict): Django session object to store answers
    
    Returns:
        tuple: (success boolean, error message)
    '''
    if current_question_id is None:
        return False, "No current question available"
    
    # Find the current question
    current_question = next((q for q in PYTHON_QUESTION_LIST if q['id'] == current_question_id), None)
    
    if not current_question:
        return False, "Invalid question ID"
    
    # Validate answer length and content
    if not answer or len(answer.strip()) == 0:
        return False, "Please provide an answer"
    
    # Initialize answers dictionary in session if not exists
    if 'quiz_answers' not in session:
        session['quiz_answers'] = {}
    
    # Store user's answer
    session['quiz_answers'][current_question_id] = {
        'user_answer': answer,
        'is_correct': answer == current_question['correct_answer']
    }
    
    return True, ""

def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    
    Args:
        current_question_id (int): ID of the current question
    
    Returns:
        tuple: (next question text or None, next question ID or None)
    '''
    # If no current question, start from the first one
    if current_question_id is None:
        first_question = PYTHON_QUESTION_LIST[0]
        return first_question['question'], first_question['id']
    
    # Find the current question's index
    current_index = next((index for (index, q) in enumerate(PYTHON_QUESTION_LIST) if q['id'] == current_question_id), -1)
    
    # Check if we're at the last question
    if current_index == len(PYTHON_QUESTION_LIST) - 1:
        return None, None
    
    # Get the next question
    next_question = PYTHON_QUESTION_LIST[current_index + 1]
    return next_question['question'], next_question['id']

def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    
    Args:
        session (dict): Django session containing quiz answers
    
    Returns:
        str: Final result message with score and performance description
    '''
    if 'quiz_answers' not in session:
        return "No answers recorded. Please complete the quiz."
    
    answers = session['quiz_answers']
    total_questions = len(PYTHON_QUESTION_LIST)
    correct_answers = sum(1 for answer in answers.values() if answer['is_correct'])
    
    # Calculate percentage
    score_percentage = (correct_answers / total_questions) * 100
    
    # Performance descriptions
    if score_percentage == 100:
        performance = "Excellent! You're a Python pro!"
    elif score_percentage >= 75:
        performance = "Great job! You have a solid understanding of Python."
    elif score_percentage >= 50:
        performance = "Good effort. You're on the right track with Python."
    else:
        performance = "Keep learning! There's room for improvement in your Python knowledge."
    
    # Detailed results
    result_message = (
        f"Quiz Completed!\n"
        f"Total Questions: {total_questions}\n"
        f"Correct Answers: {correct_answers}\n"
        f"Score: {score_percentage:.1f}%\n"
        f"{performance}"
    )
    
    return result_message
