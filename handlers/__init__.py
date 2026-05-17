from maxo.routing.routers.simple import Router

from . import interactive_tests, main_menu, mini_tests, misc, quizzes

router = Router()

router.include_router(main_menu.router)
router.include_router(misc.router)
router.include_router(interactive_tests.router)
router.include_router(mini_tests.router)
router.include_router(quizzes.router)
