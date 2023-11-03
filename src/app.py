from __future__ import annotations
from enum import Enum
from typing import Any

import flet as ft

from .components.navigation_bar import NavBar
from .context import AppContext, Orientation, Size
from .pages.base import QPage
from .pages.deck_page import DeckPage
from .pages.game.play_page import GamePlayPage
from .pages.game_page import GamePage
from .pages.not_found_page import NotFoundPage
from .qcomp import QItem, QAlign, QAnchor
from .routes import Route


class DgisimApp():
    def __init__(self, page: ft.Page):
        self._context = AppContext(
            current_route=Route.GAME,
            orientation=Orientation.PORTRAIT,
            page=page,
            reference_size=Size(page.width, page.height),
        )
        self._context.on_orientation_changed_end.add(lambda _: page.update())
        self._page = page
        self._page.title = "Dottore GISim"
        self._page.padding = 10
        self._page.navigation_bar = NavBar(context=self._context)
        self._page.on_resize = self.on_resize
        self._pages: dict[Route, QPage] = {
            Route.DECK: DeckPage,
            Route.GAME: GamePage,
            # Route.GAME_PLAY: GamePlayPage,
            Route.NOT_FOUND: NotFoundPage,
        }
        self._root_item = QItem.init_page(self._page)
        self._root_item.object_name = "root-item"

        def on_context_route_changed(route: Route) -> None:
            self.navigate(route)

        self._context.on_current_route_changed.add(on_context_route_changed)
        self._context.on_reference_size_changed_end.add(lambda _: self._page.update())

    def on_resize(self, _: ft.Page) -> None:
        wh_ratio = self._page.width / self._page.height
        if self._context.orientation is Orientation.LANDSCAPE and wh_ratio < 1:
            self._context.orientation = Orientation.PORTRAIT
        elif self._context.orientation is Orientation.PORTRAIT and wh_ratio > 1:
            self._context.orientation = Orientation.LANDSCAPE
        self._context.reference_size = Size(self._page.width, self._page.height)

    def navigate(self, route: Route) -> None:
        self._root_item.clear()
        self._root_item.add_children(page := self._get_page_at_route(route)(
            anchor=QAnchor(left=0.0, top=0.0, right=1.0, bottom=1.0),
        ))
        page.post_init(self._context)
        self._page.update()

    def _get_page_at_route(self, route: Route) -> type[QPage]:
        if route in self._pages:
            print("get page at", route)
            return self._pages[route]
        assert Route.NOT_FOUND in self._pages
        print("get page not found")
        return self._pages[Route.NOT_FOUND]
