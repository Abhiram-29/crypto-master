from pydantic import ValidationError
import pytest

# Valid test cases
#Pydantic Schema validation tests

def test_valid_mcq():
    valid_mcq = {
        "_id": 1,
        "topic": "Python",
        "difficulty": "medium",
        "hint": "Think about data types",
        "question": "What is the output of type(1/2) in Python 3?",
        "options": ["int", "float", "double", "decimal"],
        "correct_ans": "float"
    }
    
    question = MCQ(**valid_mcq)
    assert question.question_id == 1
    assert question.correct_ans == "float"
    assert question.question_type == "mcq"

def test_valid_fib():
    valid_fib = {
        "_id": 2,
        "topic": "Python Basics",
        "difficulty": "easy",
        "hint": None,
        "question": "Python is a ____ language.",
        "correct_ans": "dynamically typed"
    }
    
    question = FillInTheBlanks(**valid_fib)
    assert question.question_id == 2
    assert question.question_type == "fib"

def test_valid_mcq_with_image():
    valid_mcq_image = {
        "_id": 3,
        "topic": "Data Structures",
        "difficulty": "hard",
        "hint": "Look at the tree structure",
        "question": "What type of tree is shown in the image?",
        "options": ["Binary", "AVL", "Red-Black", "B-Tree"],
        "correct_ans": 2
    }
    
    question = MCQWithImage(**valid_mcq_image)
    assert question.correct_ans == 2
    assert question.question_type == "mcq_image"

def test_valid_wordle():
    valid_wordle = {
        "_id": 4,
        "topic": "Vocabulary",
        "difficulty": "jackpot",
        "hint": "Related to programming",
        "word": "code"  # Changed to 4-letter word
    }
    
    question = Wordle(**valid_wordle)
    assert question.word == "code"
    assert question.question_type == "wordle"

# Invalid test cases
def test_invalid_difficulty():
    with pytest.raises(ValidationError):
        MCQ(
            _id=1,
            topic="Python",
            difficulty="super-hard",  # Invalid difficulty
            question="What is Python?",
            options=["A", "B", "C", "D"],
            correct_ans="A"
        )

def test_invalid_mcq_options():
    with pytest.raises(ValidationError):
        MCQ(
            _id=1,
            topic="Python",
            difficulty="easy",
            question="What is Python?",
            options=["A", "B", "C"],  # Only 3 options
            correct_ans="A"
        )

def test_invalid_mcq_correct_ans():
    with pytest.raises(ValidationError):
        MCQ(
            _id=1,
            topic="Python",
            difficulty="easy",
            question="What is Python?",
            options=["A", "B", "C", "D"],
            correct_ans="E"  # Answer not in options
        )

def test_invalid_mcq_with_image_correct_ans():
    with pytest.raises(ValidationError):
        MCQWithImage(
            _id=1,
            topic="Python",
            difficulty="easy",
            question="What is shown?",
            options=["A", "B", "C", "D"],
            correct_ans=5  # Out of range (should be 1-4)
        )

def test_invalid_wordle_word():
    with pytest.raises(ValidationError):
        Wordle(
            _id=1,
            topic="Vocabulary",
            difficulty="easy",
            word="python"  # Too long (6 letters)
        )

if __name__ == "__main__":
    # Run all test functions
    test_functions = [
        test_valid_mcq,
        test_valid_fib,
        test_valid_mcq_with_image,
        test_valid_wordle,
        test_invalid_difficulty,
        test_invalid_mcq_options,
        test_invalid_mcq_correct_ans,
        test_invalid_mcq_with_image_correct_ans
    ]
    
    for test in test_functions:
        try:
            test()
            print(f"✅ {test.__name__} passed")
        except Exception as e:
            print(f"❌ {test.__name__} failed: {str(e)}")