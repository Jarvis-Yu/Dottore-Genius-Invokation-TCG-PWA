from __future__ import annotations
from typing import Any

import flet as ft

from ..components.wip import WIP
from ..context import AppContext, GamePlaySettings
from ..routes import Route


class GamePage(ft.Stack):
    def __init__(self, context: AppContext, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._context = context
        context.page.bgcolor = context.settings.view_bg_colour
        context.page.navigation_bar.visible = True
        self.expand = True
        self._common_content = ft.Stack(expand=True)
        self.controls.append(ft.Container(content=self._common_content, padding=10))
        button_col = {"sm": 6, "lg": 4, "xl": 3}
        self._responsive_rows = ft.ResponsiveRow([
            ft.ElevatedButton(
                text="Random PVE",
                col=button_col,
                on_click=self.goto_random_PVE,
                style=context.settings.button_style,
            ),
            ft.ElevatedButton(
                text="WIP",
                col=button_col,
                style=context.settings.button_style
            ),
        ])
        self._common_content.controls.append(self._responsive_rows)

    def goto_random_PVE(self, _: Any) -> None:
        self._context.game_mode = GamePlaySettings.from_random_PVE()
        self._context.current_route = Route.GAME_PLAY
