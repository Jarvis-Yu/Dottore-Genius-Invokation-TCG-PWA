from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Literal

import flet as ft
from dgisim import Pid

from .routes import Route


class AddSensitiveSet(set):
    def __init__(self, on_added: Callable[[Callable], Any], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._on_added = on_added

    def add(self, item: Callable):
        super().add(item)
        self._on_added(item)


class Orientation(Enum):
    LANDSCAPE = "Landscape"
    PORTRAIT = "Portrait"


@dataclass(kw_only=True)
class Settings:
    theme_colour: str = "#6A8096"
    theme_colour_dark: str = "#56676E"
    theme_colour_light: str = "#88B1Bf"
    view_bg_colour: str = theme_colour_dark
    nav_bar_colour: str = theme_colour
    normal_text_colour: str = "#FFFFFF"
    contrast_text_colour: str = "#000000"

    @property
    def button_style(self) -> ft.ButtonStyle:
        return ft.ButtonStyle(
            color={
                ft.MaterialState.HOVERED: self.contrast_text_colour,
                ft.MaterialState.DEFAULT: self.normal_text_colour,
            },
            bgcolor={
                ft.MaterialState.HOVERED: self.theme_colour_light,
                ft.MaterialState.DEFAULT: self.theme_colour
            },
        )


@dataclass(kw_only=True)
class PlayerSettings:
    type: Literal["P", "E"]


@dataclass(kw_only=True)
class GamePlaySettings:
    primary_player: Pid
    primary_settings: PlayerSettings
    oppo_settings: PlayerSettings
    completely_random: bool = False

    @classmethod
    def from_random_PVE(cls) -> None:
        return GamePlaySettings(
            primary_player=Pid.P1,
            primary_settings=PlayerSettings(type="P"),
            oppo_settings=PlayerSettings(type="E"),
            completely_random=True,
        )


class AppContext:
    def __init__(
            self,
            current_route: Route,
            orientation: Orientation,
            page: ft.Page,
            settings: Settings = Settings(),
    ) -> None:
        self._current_route = current_route
        self._game_mode: None | GamePlaySettings = None
        self._on_curr_route_changed: set[Callable[[Route], None]] = AddSensitiveSet(
            lambda f: f(self._current_route)
        )
        self._orientation = orientation
        self._on_orientation_changed: set[Callable[[Orientation], None]] = AddSensitiveSet(
            lambda f: f(self._orientation)
        )
        self._on_orientation_changed_end: set[Callable[[Orientation], None]] = AddSensitiveSet(
            lambda f: f(self._orientation)
        )
        self._page = page
        self._settings = settings

    @property
    def current_route(self) -> Route:
        return self._current_route

    @current_route.setter
    def current_route(self, new_route: Route) -> None:
        if (self._current_route is new_route):
            return
        self._current_route = new_route
        for on_curr_route_changed in self._on_curr_route_changed:
            on_curr_route_changed(self._current_route)

    @property
    def game_mode(self) -> GamePlaySettings:
        assert self._game_mode is not None
        return self._game_mode

    @game_mode.setter
    def game_mode(self, new_mode: GamePlaySettings) -> None:
        self._game_mode = new_mode

    @property
    def on_current_route_changed(self) -> set[Callable[[Route], None]]:
        return self._on_curr_route_changed

    @property
    def orientation(self) -> Orientation:
        return self._orientation

    @orientation.setter
    def orientation(self, new_orientation: Orientation) -> None:
        if self._orientation is new_orientation:
            return
        self._orientation = new_orientation
        print("Orientation:", new_orientation.value)
        for f in self._on_orientation_changed:
            f(new_orientation)
        for f in self._on_orientation_changed_end:
            f(new_orientation)

    @property
    def on_orientation_changed(self) -> set[Callable[[Orientation], None]]:
        return self._on_orientation_changed

    @property
    def on_orientation_changed_end(self) -> set[Callable[[Orientation], None]]:
        return self._on_orientation_changed_end

    @property
    def page(self) -> ft.Page:
        return self._page

    @property
    def settings(self) -> Settings:
        return self._settings
