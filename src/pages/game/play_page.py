from __future__ import annotations
from typing import Any

import flet as ft

from ...components.wip import WIP
from ...context import AppContext, GamePlaySettings
from ...routes import Route


class GamePlayPage(ft.Stack):
    def __init__(self, context: AppContext, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._context = context
        context.page.bgcolor = context.settings.view_bg_colour
        context.page.navigation_bar.visible = False
        self.expand = True
        self._common_content = ft.Stack(expand=True)
        self.controls.append(WIP(context))
        self.controls.append(ft.Container(content=self._common_content, padding=10))

        def back_to_home(_: Any) -> None:
            context.current_route = Route.GAME

        self._common_content.controls.append(
            ft.Container(
                content=ft.IconButton(
                    icon=ft.icons.EXIT_TO_APP,
                    on_click=back_to_home,
                    style=context.settings.button_style,
                ),
                alignment=ft.alignment.top_right,
            )
        )
