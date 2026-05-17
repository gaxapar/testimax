from maxo.routing.filters.payload import Payload


class InteractiveTestsList(Payload, prefix="interactive_tests_list"):
    page: int


class OpenInteractiveTest(Payload, prefix="open_interactive_test"):
    slug: str


class ProceedInteractiveTest(Payload, prefix="proceed_interactive_test"):
    slug: str


class InteractiveTestOption(Payload, prefix="interactive_test_option"):
    slug: str
    question_index: int
    option_index: int
