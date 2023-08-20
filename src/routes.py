from __future__ import annotations
from enum import Enum


class Route(Enum):
    HOME = "/"
    GAME = "/game"
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
