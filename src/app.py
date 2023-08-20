from __future__ import annotations
import asyncio
from enum import Enum

import flet as ft

from .context import AppContext
from .pages.deck_page import DeckPage
from .pages.game_page import GamePage
from .pages.not_found_page import NotFoundPage
from .routes import Route


class DgisimApp():
    def __init__(self, page: ft.Page):
        self._context = AppContext(
            current_route=Route.GAME,
        )
        self._page = page
        self._page.title = "Dottore GISim"
        self._page.on_route_change = self._on_route_change_set_view
        self._views: dict[Route, type[ft.View]] = {
            Route.DECK: DeckPage,
            Route.GAME: GamePage,
            Route.NOT_FOUND: NotFoundPage,
        }

        def on_context_route_changed(route: Route) -> None:
            self.navigate(route)
        self._context.on_current_route_changed = on_context_route_changed

        asyncio.run(self.run())

    @property
    def context(self) -> AppContext:
        return self._context

    @property
    def page(self) -> ft.Page:
        return self._page

    @property
    def navigation_bar(self) -> ft.NavigationBar:
        return self._navigation_bar

    def navigate(self, route: Route) -> None:
        self._page.go(route.value)

    def _on_route_change_set_view(self, _: ft.RouteChangeEvent) -> None:
        self._page.views.clear()
        view = self._get_view_at_route(Route.find_route(self._page.route))
        self._page.views.append(view)
        self._page.update()

    def _get_view_at_route(self, route: Route) -> ft.View:
        if route in self._views:
            return self._views[route](self._context)
        assert Route.NOT_FOUND in self._views
        return self._views[Route.NOT_FOUND](self._context)

    async def run(self):
        asyncio.create_task(self.auto_refresh())
        while True:
            await asyncio.sleep(0x7fffffff)

    async def auto_refresh(self):
        return
        while True:
            self._page.update()
            await asyncio.sleep(0.04)
