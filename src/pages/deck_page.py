from __future__ import annotations

import flet as ft

from ..components.wip import WIP
from ..context import AppContext


class DeckPage(ft.Stack):
    def __init__(self, context: AppContext, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._context = context
        context.page.bgcolor = context.settings.view_bg_colour
        self.expand = True
        self.controls.append(WIP(context))
