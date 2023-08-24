from __future__ import annotations
from enum import Enum

import flet as ft

from .components.navigation_bar import NavBar
from .context import AppContext
from .pages.deck_page import DeckPage
from .pages.game_page import GamePage
from .pages.not_found_page import NotFoundPage
from .routes import Route


class DgisimApp():
    def __init__(self, page: ft.Page):
        self._context = AppContext(
            current_route=Route.GAME,
            page=page,
        )
        self._page = page
        self._page.title = "Dottore GISim"
        self._page.navigation_bar = NavBar(context=self._context)
        self._page.padding = 0
        self._pages: dict[Route, type[ft.Stack]] = {
            Route.DECK: DeckPage,
            Route.GAME: GamePage,
            Route.NOT_FOUND: NotFoundPage,
        }

        def on_context_route_changed(route: Route) -> None:
            self.navigate(route)
        self._context.add_on_current_route_changed(on_context_route_changed)

    def navigate(self, route: Route) -> None:
        # self._page.go(route.value)
        self._page.controls.clear()
        self._page.controls.append(self._get_page_at_route(route))
        self._page.update()

    def _get_page_at_route(self, route: Route) -> ft.Stack:
        if route in self._pages:
            print("get page at", route)
            return self._pages[route](self._context)
        assert Route.NOT_FOUND in self._pages
        print("get page not found")
        return self._pages[Route.NOT_FOUND](self._context)
