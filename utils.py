import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypedDict

import yaml
from maxo import Bot

logger = logging.getLogger(__name__)


class MiniTestAnswer(TypedDict):
    text: str
    photo_file_id: str | None


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
