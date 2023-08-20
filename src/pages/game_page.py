from __future__ import annotations

import flet as ft

from ..components.navigation_bar import NavBar
from ..context import AppContext
from ..routes import Route

class GamePage(ft.View):
    def __init__(self, context: AppContext, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._context = context
        self.bgcolor = self._context.settings.theme_colour_dark
        self.controls.append(ft.Text("Game"))
        def set_route_not_found(e) -> None:
            self._context.current_route = Route.NOT_FOUND
        self.controls.append(ft.TextButton(text="Not Found", on_click=set_route_not_found))
        self.navigation_bar = NavBar(context=self._context)