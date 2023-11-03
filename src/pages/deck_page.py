from __future__ import annotations

import flet as ft

from ..components.wip import WIP
from ..qcomp import QItem, QAnchor, QInset
from ..context import AppContext
from .base import QPage


class DeckPage(QPage):
    def post_init(self, context: AppContext) -> None:
        self._context = context
        context.page.bgcolor = context.settings.view_bg_colour
        context.page.navigation_bar.visible = True
        self.add_flet_comp(WIP(context))
