from __future__ import annotations

import flet as ft

from ..components.navigation_bar import NavBar
from ..context import AppContext
from ..qcomp import QItem, QAnchor, QInset
from .base import QPage


class NotFoundPage(QPage):
    def post_init(self, context: AppContext) -> None:
        self._context = context
        context.page.bgcolor = self._context.settings.view_bg_colour
        context.page.navigation_bar = NavBar(context=self._context)
        self.inset = QInset(bottom=context.settings.nav_bar_height)
        self._recalc_size()
        self._update_internal_container_on_size()
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
