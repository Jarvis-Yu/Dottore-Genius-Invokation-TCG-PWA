from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable

from .routes import Route


@dataclass(kw_only=True)
class Settings:
    theme_colour: str = "#6A8096"
    theme_colour_dark: str = "#56676E"
    theme_colour_light: str = "#88B1Bf"


# @dataclass(kw_only=True)
class AppContext:
    def __init__(
            self,
            current_route: Route,
            settings: Settings = Settings(),
    ) -> None:
        self._current_route = current_route
        self._on_curr_route_changed: Callable[[Route], None] = lambda _: None
        self._settings = settings

    @property
    def current_route(self) -> Route:
        return self._current_route

    @current_route.setter
    def current_route(self, new_route: Route) -> None:
        if (self._current_route is new_route):
            return
        self._current_route = new_route
        self._on_curr_route_changed(self._current_route)

    @property
    def on_current_route_changed(self) -> Route:
        return self._on_curr_route_changed

    @on_current_route_changed.setter
    def on_current_route_changed(self, f: Callable[[Route], None]) -> None:
        self._on_curr_route_changed = f
        self._on_curr_route_changed(self._current_route)

    @property
    def settings(self) -> Settings:
        return self._settings

    # settings: Settings = Settings()
    # current_route: Route
    # _version: int = 0
    # _versions: dict[str, int] = defaultdict(int)

    # @property
    # def version(self) -> int:
    #     return self._version

    # def __setattr__(self, name: str, value: Any) -> None:
    #     super().__setattr__(name, value)
    #     self._versions[name] += 1

    # def update_done(self) -> None:
    #     self._version += 1
    #     for handlers in self._listeners.values():
    #         handlers()

    # _listeners: dict[int, Callable] = {}

    # def register(self, obj: object, on_context_change: Callable[[], None]) -> None:
    #     self._listeners[id(obj)] = on_context_change

    # def unregister(self, obj: object) -> None:
    #     if id(obj) in self._listeners:
    #         del self._listeners[obj]