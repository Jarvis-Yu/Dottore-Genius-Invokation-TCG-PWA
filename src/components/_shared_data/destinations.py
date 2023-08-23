from dataclasses import dataclass

import flet as ft

from ...routes import Route


@dataclass
class Destination:
    index: int
    route: Route
    icon: str
    label: str


DESTINATIONS = [
    Destination(0, Route.GAME, ft.icons.GAMEPAD_ROUNDED, "Game"),
    Destination(1, Route.DECK, ft.icons.CONTENT_COPY_OUTLINED, "Decks")
]
