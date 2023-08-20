from __future__ import annotations

import flet as ft

from ..components.navigation_bar import NavBar
from ..context import AppContext


class DeckPage(ft.View):
    def __init__(self, context: AppContext, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._context = context
        self.bgcolor = self._context.settings.theme_colour_dark
        self.controls.append(ft.Text("Deck"))
        self.navigation_bar = NavBar(context=self._context)
