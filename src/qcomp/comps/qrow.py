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
import flet as ft
from typing import Sequence

from typing_extensions import Self

from .qitem import *

class QRow(QItem):
    def __init__(
        self,
        object_name: str = "QRow",
        parent: Self | None = None,
        width: int | None = None,
        height: int | None = None,
        width_pct: float | None = None,
        height_pct: float | None = None,
        expand: bool = False,
        align: QAlign | ft.Alignment | None = None,
        anchor: QAnchor | None = None,
        clip: ft.ClipBehavior = ft.ClipBehavior.NONE,
        colour: str = ft.colors.with_opacity(0, "#FFFFFF"),
        border: ft.Border | None = None,
        children: Sequence[Self] | Self = (),
        spacing: float = 0.0,
    ):
        super().__init__(
            object_name=object_name,
            parent=parent,
            width=width,
            height=height,
            width_pct=width_pct,
            height_pct=height_pct,
            expand=expand,
            align=align,
            anchor=anchor,
            clip=clip,
            colour=colour,
            border=border,
        )
        self.spacing = 0.0
