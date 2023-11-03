from dataclasses import dataclass

import flet as ft

from ..context import AppContext
from ..routes import Route
from ._shared_data.destinations import DESTINATIONS


class NavBar(ft.NavigationBar):
    def __init__(self, context: AppContext, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._context = context
        self.height = context.settings.nav_bar_height
        self.bgcolor = context.settings.nav_bar_colour
        self.destinations = [
            ft.NavigationDestination(icon=dest.icon, label=dest.label)
            for dest in DESTINATIONS
        ]
        self.selected_index = self.find_index_by_route(self._context.current_route)
        self.on_change = self.on_index_changed
        context.on_current_route_changed.add(self.sync_destination)

    def find_index_by_route(self, route: Route) -> int:
        for dest in DESTINATIONS:
            if dest.route is route:
                return dest.index
        return -1

    def find_route_by_index(self, index: int) -> Route:
        for dest in DESTINATIONS:
            if dest.index == index:
                return dest.route
        return Route.NOT_FOUND

    def sync_destination(self, route: Route) -> None:
        curr_index = self.find_index_by_route(route)
        if self.selected_index != curr_index:
            self.selected_index = curr_index
            self._context.page.update()

    def on_index_changed(self, e) -> None:
        new_route = self.find_route_by_index(self.selected_index)
        if new_route != self._context.current_route:
            self._context.current_route = new_route
