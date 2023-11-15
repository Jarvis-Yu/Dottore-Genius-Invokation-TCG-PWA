"""
This file is part of Dottore Genius Invokation PWA.

Dottore Genius Invokation PWA is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option)
any later version.

Dottore Genius Invokation PWA is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
Dottore Genius Invokation PWA. If not, see <https://www.gnu.org/licenses/>
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
