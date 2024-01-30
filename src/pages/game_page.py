"""
This file is part of Dottore Genius Invokation PWA.

Dottore Genius Invokation PWA is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option)
any later version.

Dottore Genius Invokation PWA is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
Dottore Genius Invokation PWA. If not, see <https://www.gnu.org/licenses/>
"""
from __future__ import annotations
from typing import Any

import flet as ft
import dgisim
from qlet import QItem, QAnchor, QInset, QText, QAlign

from ..components.navigation_bar import NavBar
from ..components.wip import WIP
from ..context import AppContext, GamePlaySettings
from ..routes import Route
from .base import QPage


class GamePage(QPage):
    def post_init(self, context: AppContext) -> None:
        self._context = context
        context.page.bgcolor = self._context.settings.view_bg_colour
        context.page.navigation_bar.visible = True
        self.inset = QInset(bottom=context.settings.nav_bar_height)
        self.update_size()
        button_col = {"sm": 6, "lg": 4, "xl": 3}
        self._responsive_rows = ft.ResponsiveRow([
            ft.ElevatedButton(
                text="Random PVE",
                col=button_col,
                on_click=self.goto_random_PVE,
                style=context.settings.button_style,
            ),
            ft.ElevatedButton(
                text="Random Local PVP",
                col=button_col,
                on_click=self.goto_random_local_PVP,
                style=context.settings.button_style,
            ),
            # ft.ElevatedButton(
            #     text="Random EVE",
            #     col=button_col,
            #     on_click=self.goto_random_EVE,
            #     style=context.settings.button_style,
            # ),
            # ft.ElevatedButton(
            #     text="WIP",
            #     col=button_col,
            #     style=context.settings.button_style
            # ),
        ])
        self.add_flet_comp(self._responsive_rows)
        self.add_children(QText(
            text=f"used dgisim version {dgisim.__version__}",
            text_colour="#888888",
            width_pct=1,
            height_pct=0.03,
            anchor=QAnchor(left=0, bottom=1),
            size_rel_height=0.5,
        ))

    def goto_random_PVE(self, _: Any) -> None:
        self._context.game_mode = GamePlaySettings.from_random_PVE()
        self._context.game_data.init_game()
        self._context.current_route = Route.GAME_PLAY

    def goto_random_local_PVP(self, _: Any) -> None:
        self._context.game_mode = GamePlaySettings.from_random_local_PVP()
        self._context.game_data.init_game()
        self._context.current_route = Route.GAME_PLAY

    def goto_random_EVE(self, _: Any) -> None:
        self._context.game_mode = GamePlaySettings.from_random_EVE()
        self._context.game_data.init_game()
        self._context.current_route = Route.GAME_PLAY
