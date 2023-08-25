from __future__ import annotations
from enum import Enum
from typing import Any

import flet as ft

from .components.navigation_bar import NavBar
from .context import AppContext, Orientation
from .pages.deck_page import DeckPage
from .pages.game_page import GamePage
from .pages.not_found_page import NotFoundPage
from .routes import Route


class DgisimApp():
    def __init__(self, page: ft.Page):
        self._context = AppContext(
            current_route=Route.GAME,
            orientation=Orientation.PORTRAIT,
            page=page,
        )
        self._context.on_orientation_changed_end.add(lambda _: page.update())
        self._page = page
        self._page.navigation_bar = NavBar(context=self._context)
        self._page.on_resize = self.on_resize
        self._page.padding = 0
        self._page.title = "Dottore GISim"
        self._pages: dict[Route, type[ft.Stack]] = {
            Route.DECK: DeckPage,
            Route.GAME: GamePage,
            Route.NOT_FOUND: NotFoundPage,
        }
        self._safe_area = ft.SafeArea(expand=True)
        self._page.controls.append(self._safe_area)

        def on_context_route_changed(route: Route) -> None:
            self.navigate(route)
        self._context.on_current_route_changed.add(on_context_route_changed)

    def on_resize(self, _: ft.Page) -> None:
        wh_ratio = self._page.window_width / self._page.window_height
        if self._context.orientation is Orientation.LANDSCAPE and wh_ratio < 1:
            self._context.orientation = Orientation.PORTRAIT
        elif self._context.orientation is Orientation.PORTRAIT and wh_ratio > 1:
            self._context.orientation = Orientation.LANDSCAPE

    def navigate(self, route: Route) -> None:
        self._safe_area.content = self._get_page_at_route(route)
        self._page.update()

    def _get_page_at_route(self, route: Route) -> ft.Stack:
        if route in self._pages:
            print("get page at", route)
            return self._pages[route](self._context)
        assert Route.NOT_FOUND in self._pages
        print("get page not found")
        return self._pages[Route.NOT_FOUND](self._context)
