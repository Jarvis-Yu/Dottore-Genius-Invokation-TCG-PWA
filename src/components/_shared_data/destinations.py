"""
Copyright (C) 2024 Leyang Yu

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from dataclasses import dataclass

import flet as ft

from ...routes import Route


@dataclass
class Destination:
    index: int
    route: Route
    icon: str
    label: str


DESTINATIONS = [
    Destination(0, Route.GAME, ft.icons.GAMEPAD_ROUNDED, "Game"),
    Destination(1, Route.DECK, ft.icons.CONTENT_COPY_OUTLINED, "Decks")
]
