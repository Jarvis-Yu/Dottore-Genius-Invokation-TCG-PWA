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
