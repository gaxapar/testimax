from .base import Base
from .mini_test import MiniTest
from .mini_test_answer import MiniTestAnswer
from .quiz import Quiz
from .quiz_answer import QuizAnswer
from .quiz_question import QuizQuestion
from .user import User

AnyModel = MiniTest | MiniTestAnswer | User | Quiz | QuizQuestion | QuizAnswer

__all__ = ("AnyModel", "Base", "MiniTest", "MiniTestAnswer", "Quiz", "QuizAnswer", "QuizQuestion", "User")
