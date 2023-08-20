from dataclasses import dataclass

import flet as ft

from ..context import AppContext
from ..routes import Route

@dataclass
class Destination:
    index: int
    route: Route
    icon: str
    label: str

class NavBar(ft.NavigationBar):
    def __init__(self, context: AppContext, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._context = context
        self.bgcolor = context.settings.theme_colour
        self._destination_data = [
            Destination(0, Route.GAME, ft.icons.GAMEPAD_ROUNDED, "Game"),
            Destination(1, Route.DECK, ft.icons.CONTENT_COPY_OUTLINED, "Decks")
        ]
        self.destinations=[
            ft.NavigationDestination(icon=dest.icon, label=dest.label)
            for dest in self._destination_data
        ]
        self.selected_index = self.find_index_by_route(self._context.current_route)
        self.on_change = self.on_index_changed

    def find_index_by_route(self, route: Route) -> int:
        for dest in self._destination_data:
            if dest.route is route:
                return dest.index
        return -1

    def find_route_by_index(self, index: int) -> Route:
        for dest in self._destination_data:
            if dest.index == index:
                return dest.route
        return Route.NOT_FOUND

    def on_index_changed(self, e) -> None:
        self._context.current_route = self.find_route_by_index(self.selected_index)