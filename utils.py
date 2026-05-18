import logging
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import NotRequired, TypedDict

import yaml
from maxo import Bot

from database import models

logger = logging.getLogger(__name__)


class MiniTestAnswer(TypedDict):
    text: str
    photo_file_id: str | None


class QuizAnswerDict(TypedDict):
    text: str
    is_correct: NotRequired[bool]


class QuizQuestionDict(TypedDict):
    text: str
    photo_file_id: str | None
    answers: list[QuizAnswerDict]


# UI markers for quiz answers
QUIZ_ANSWER_CORRECT_MARK = "✅"
QUIZ_ANSWER_NEUTRAL_MARK = "•"


def quiz_answer_correct_marker() -> str:
    """Return the correct-answer marker including trailing space."""
    return f"{QUIZ_ANSWER_CORRECT_MARK} "


def quiz_answer_neutral_marker() -> str:
    """Return the neutral-answer marker including trailing space."""
    return f"{QUIZ_ANSWER_NEUTRAL_MARK} "


@dataclass
class TestResult:
    slug: str
    description: str


@dataclass
class TestOption:
    text: str
    points: dict[str, int]


@dataclass
class TestQuestion:
    question: str
    photo: str
    options: list[TestOption]


@dataclass
class InteractiveTest:
    slug: str
    title: str
    photo: str
    description: str
    results: list[TestResult] = field(default_factory=list)
    questions: list[TestQuestion] = field(default_factory=list)


def load_interactive_test(path: Path) -> InteractiveTest:
    with path.open() as file:
        data = yaml.safe_load(file)

    results = [TestResult(slug=r["slug"], description=r["description"]) for r in data["results"]]

    questions = [
        TestQuestion(
            question=q["question"],
            photo=q["photo"],
            options=[TestOption(text=o["text"], points=o["points"]) for o in q["options"]],
        )
        for q in data["questions"]
    ]

    return InteractiveTest(
        slug=data["slug"],
        title=data["title"],
        photo=data["photo"],
        description=data["description"],
        results=results,
        questions=questions,
    )


async def is_subbed(bot: Bot, user_id: int, channels: list[dict[str, int]]) -> bool:
    for channel in channels:
        members_list = await bot.get_members(chat_id=channel["id"], user_ids=[user_id])

        if not members_list.members:
            return False

    return True


# Formatting helpers for quizzes


def format_question_list(questions: Sequence[str]) -> str:
    if not questions:
        return ""

    return "\n".join(f"{index}. {question}" for index, question in enumerate(questions, start=1))


def format_answer_list(answers: Sequence[models.QuizAnswer]) -> str:
    if not answers:
        return "Ответов пока нет"

    return "\n".join(
        (
            f"{index}. {quiz_answer_correct_marker()}{answer.text}"
            if answer.is_correct
            else f"{index}. {quiz_answer_neutral_marker()}{answer.text}"
        )
        for index, answer in enumerate(answers, start=1)
    )


def build_quiz_question_editor_text(question: models.QuizQuestion, answers: Sequence[models.QuizAnswer]) -> str:
    return f"<b>Вопрос:</b> {question.text}\n\n<b>Ответы:</b>\n{format_answer_list(answers)}"
