from __future__ import annotations

import flet as ft

from ..components.navigation_bar import NavBar
from ..context import AppContext
from ..routes import Route

class GamePage(ft.Stack):
    def __init__(self, context: AppContext, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._context = context
        context.page.bgcolor = context.settings.theme_colour_dark
        self.expand = True
        self.controls.append(ft.Text("Game"))