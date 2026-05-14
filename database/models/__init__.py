from .base import Base
from .mini_test import MiniTest
from .mini_test_answer import MiniTestAnswer
from .user import User

AnyModel = MiniTest | MiniTestAnswer | User

__all__ = ("Base", "MiniTest", "MiniTestAnswer", "User", "AnyModel")
