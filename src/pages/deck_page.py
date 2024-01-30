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

import flet as ft
from qlet import QItem, QAnchor, QInset

from ..components.wip import WIP
from ..context import AppContext
from .base import QPage


class DeckPage(QPage):
    def post_init(self, context: AppContext) -> None:
        self._context = context
        context.page.bgcolor = context.settings.view_bg_colour
        context.page.navigation_bar.visible = True
        self.add_flet_comp(WIP(context))
