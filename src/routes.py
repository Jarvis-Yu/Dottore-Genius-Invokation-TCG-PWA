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
from __future__ import annotations
from enum import Enum


class Route(Enum):
    HOME = "/"
    GAME = "/game"
    GAME_PLAY = "/game/play"
    DECK = "/deck"
    NOT_FOUND = "/not-found"

    @classmethod
    def find_route(cls, route: str) -> Route:
        print(f"{cls.__name__}::find_route::[try-find]{route}")
        for r in cls:
            if r.value == route:
                print(f"{cls.__name__}::find_route::[found]{r}")
                return r
        print(f"{cls.__name__}::find_route::[found]{cls.NOT_FOUND}")
        return cls.NOT_FOUND
