from __future__ import annotations
from typing import Any

import flet as ft

from ..components.navigation_bar import NavBar
from ..components.wip import WIP
from ..context import AppContext, GamePlaySettings
from ..qcomp import QItem, QAnchor, QInset
from ..routes import Route
from .base import QPage


class GamePage(QPage):
    def post_init(self, context: AppContext) -> None:
        self._context = context
        context.page.bgcolor = self._context.settings.view_bg_colour
        context.page.navigation_bar.visible = True
        self.inset = QInset(bottom=context.settings.nav_bar_height)
        self._recalc_size()
        self._update_internal_container_on_size()
        button_col = {"sm": 6, "lg": 4, "xl": 3}
        self._responsive_rows = ft.ResponsiveRow([
            ft.ElevatedButton(
                text="Random PVE",
                col=button_col,
                on_click=self.goto_random_PVE,
                style=context.settings.button_style,
            ),
            ft.ElevatedButton(
                text="Random EVE",
                col=button_col,
                on_click=self.goto_random_EVE,
                style=context.settings.button_style,
            ),
            ft.ElevatedButton(
                text="WIP",
                col=button_col,
                style=context.settings.button_style
            ),
        ])
        self.add_flet_comp(self._responsive_rows)

    def goto_random_PVE(self, _: Any) -> None:
        self._context.game_mode = GamePlaySettings.from_random_PVE()
        self._context.current_route = Route.GAME_PLAY

    def goto_random_EVE(self, _: Any) -> None:
        self._context.game_mode = GamePlaySettings.from_random_EVE()
        self._context.current_route = Route.GAME_PLAY
