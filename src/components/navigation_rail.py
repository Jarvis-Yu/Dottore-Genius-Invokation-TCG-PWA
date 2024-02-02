"""
Copyright (C) 2024 Leyang Yu

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from dataclasses import dataclass

import flet as ft

from ..context import AppContext
from ..routes import Route
from ._shared_data.destinations import DESTINATIONS


class NavRail(ft.NavigationRail):
    def __init__(self, context: AppContext, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._context = context
        self.bgcolor = context.settings.nav_bar_colour
        self.destinations = [
            ft.NavigationRailDestination(icon=dest.icon, selected_icon=dest.icon, label=dest.label)
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

    def on_index_changed(self, e) -> None:
        new_route = self.find_route_by_index(self.selected_index)
        if new_route != self._context.current_route:
            self._context.current_route = new_route
