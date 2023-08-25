from __future__ import annotations

import flet as ft

from ..components.navigation_bar import NavBar
from ..context import AppContext


class NotFoundPage(ft.Stack):
    def __init__(self, context: AppContext, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._context = context
        context.page.bgcolor = self._context.settings.view_bg_colour
        context.page.navigation_bar = NavBar(context=self._context)
        self.controls.append(ft.Text("Page Not Found!"))
        self.controls.append(ft.Text("Please select a valid page from the navigation bar."))