from .base import Base
from .mini_test import MiniTest
from .mini_test_answer import MiniTestAnswer
from .quiz import Quiz
from .quiz_answer import QuizAnswer
from .quiz_question import QuizQuestion
from .referral_stats import ReferralStats
from .user import User

AnyModel = MiniTest | MiniTestAnswer | Quiz | QuizAnswer | QuizQuestion | ReferralStats | User

__all__ = (
    "AnyModel",
    "Base",
    "MiniTest",
    "MiniTestAnswer",
    "Quiz",
    "QuizAnswer",
    "QuizQuestion",
    "ReferralStats",
    "User",
)
