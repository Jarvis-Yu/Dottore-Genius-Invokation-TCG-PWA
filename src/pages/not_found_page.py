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

from ..components.navigation_bar import NavBar
from ..context import AppContext
from .base import QPage


class NotFoundPage(QPage):
    def post_init(self, context: AppContext) -> None:
        self._context = context
        context.page.bgcolor = self._context.settings.view_bg_colour
        # context.page.navigation_bar = NavBar(context=self._context)
        context.page.navigation_bar.visible = True
        self.inset = QInset(bottom=context.settings.nav_bar_height)
        self.update_size()
        self.add_flet_comp(ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("Page Not Found!"),
                        ft.Text("Please select a valid page from the navigation bar."),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        ))
        # self.add_children((
        #     QItem(
        #         width_pct=0.5,
        #         height_pct=0.1,
        #         anchor=QAnchor(left=0.25, top=0.5),
        #         colour=ft.colors.with_opacity(0.3, "#000000")
        #     ),
        #     QItem(
        #         width_pct=0.5,
        #         height_pct=0.1,
        #         anchor=QAnchor(left=0.25, top=0.6),
        #         colour=ft.colors.with_opacity(0.3, "#FF0000")
        #     ),
        #     QItem(
        #         width_pct=0.5,
        #         height_pct=0.1,
        #         anchor=QAnchor(left=0.25, top=0.7),
        #         colour=ft.colors.with_opacity(0.3, "#00FF00")
        #     ),
        #     QItem(
        #         width_pct=0.5,
        #         height_pct=0.1,
        #         anchor=QAnchor(left=0.25, top=0.8),
        #         colour=ft.colors.with_opacity(0.3, "#0000FF")
        #     ),
        # ))
