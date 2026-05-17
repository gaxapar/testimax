from maxo.routing.filters.payload import Payload


class Cancel(Payload, prefix="cancel"):
    pass


class BackToMainMenu(Payload, prefix="back_to_main_menu"):
    pass


class Empty(Payload, prefix="empty"):
    pass
