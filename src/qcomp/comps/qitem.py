from dataclasses import dataclass
from typing import Sequence

import flet as ft
from typing_extensions import Self

__all__ = [
    "QAlign",
    "QAnchor",
    "QItem",
]

def _check_only_one_holds(bools: Sequence[bool]) -> bool:
    flag = False
    for b in bools:
        if not b:
            continue
        if flag:
            print(bools)
            return False
        flag = True
    return True


@dataclass(slots=True)
class QAnchor:
    """
    Anchor borders to a side of the parent.

    Values range from 0 to 1 representing the percentage of the parent's width/height.
    (left to right, top to bottom)
    """
    left: float | None = None
    top: float | None = None
    right: float | None = None
    bottom: float | None = None


@dataclass(slots=True)
class QAlign:
    """
    Same as flet.Alignment, but with range 0 to 1 instead of -1 to 1.
    """
    x_pct: float = 0.5
    y_pct: float = 0.5

    def to_flet(self) -> ft.Alignment:
        return ft.Alignment(
            (self.x_pct - 0.5) * 2,
            (self.y_pct - 0.5) * 2,
        )


class QItem:
    def __init__(
        self,
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
    ):
        self.parent = parent
        self.width = width
        self.height = height
        self.width_pct = width_pct
        self.height_pct = height_pct
        self.expand = expand
        self.align = align if not isinstance(align, QAlign) else align.to_flet()
        self.anchor = anchor
        self.clip = clip
        self.colour = colour
        self.border = border

        assert _check_only_one_holds((
            self.anchor is not None,
            self.align is not None,
            self.expand,
        )), "Only one of anchor, align, or expand can be set"

        self.children: list[Self] = []

        self._recalc_size()
        self._init_internal_container()

        if self.parent is not None:
            self.parent._add_child_item(self)

    def _init_internal_container(self) -> None:
        self._frame = ft.Stack(
            expand=True,
            clip_behavior=self.clip,
        )
        if self.expand:
            self._container = ft.Container(
                content=self._frame,
                bgcolor=self.colour,
                expand=True,
            )
            self.root_component = ft.TransparentPointer(
                content=self._container,
                expand=True,
            )
        else:
            self._container = ft.Container(
                content=self._frame,
                bgcolor=self.colour,
                expand=True,
            )
            self.root_component = ft.TransparentPointer(
                content=ft.Container(
                    content=ft.TransparentPointer(
                        content=self._container,
                        width=self.width,
                        height=self.height,
                    ),
                    bgcolor="transparent",
                    expand=True,
                    padding=ft.Padding(
                        left=-self.width / 2,
                        top=-self.height / 2,
                        right=-self.width / 2,
                        bottom=-self.height / 2,
                    ),
                    alignment=self.align,
                ),
                expand=True,
            )
        self._container.border = self.border

    def _update_internal_container_on_size(self) -> None:
        if self.expand:
            return
        internal_container = self.root_component.content
        assert isinstance(internal_container, ft.Container)
        internal_container.padding = ft.Padding(
            left=-self.width / 2,
            top=-self.height / 2,
            right=-self.width / 2,
            bottom=-self.height / 2,
        )
        internal_container.alignment = self.align
        top_trans_container = internal_container.content
        assert isinstance(top_trans_container, ft.TransparentPointer)
        top_trans_container.width = self.width
        top_trans_container.height = self.height

    def _recalc_size(self) -> None:
        if self.width_pct is not None:
            self.width = self.parent.width * self.width_pct
        if self.height_pct is not None:
            self.height = self.parent.height * self.height_pct

        if self.anchor is not None:
            if self.anchor.left is not None and self.anchor.right is not None:
                self.width = self.parent.width * (self.anchor.right - self.anchor.left)
            if self.anchor.top is not None and self.anchor.bottom is not None:
                self.height = self.parent.height * (self.anchor.bottom - self.anchor.top)

            width_pct = self.width / self.parent.width
            height_pct = self.height / self.parent.height
            align = QAlign()
            if self.anchor.left is not None:
                align.x_pct = self.anchor.left + width_pct / 2
            if self.anchor.right is not None:
                align.x_pct = self.anchor.right - width_pct / 2
            if self.anchor.top is not None:
                align.y_pct = self.anchor.top + height_pct / 2
            if self.anchor.bottom is not None:
                align.y_pct = self.anchor.bottom - height_pct / 2
            self.align = align.to_flet()

        for child in self.children:
            child._recalc_size()
            child._update_internal_container_on_size()

    def _add_child_item(self, item: Self) -> None:
        self.children.append(item)
        self._frame.controls.append(item.root_component)

    def _add_to_page(self, page: ft.Page) -> None:
        self.width = page.window_width
        self.height = page.window_height
        page.controls.append(ft.SafeArea(
            content=self.root_component,
            expand=True,
        ))

        def on_resize(_: ft.ControlEvent) -> None:
            self.width = page.window_width
            self.height = page.window_height
            self._on_resize()
            page.update()

        page.on_resize = on_resize

    def _on_resize(self) -> None:
        for child in self.children:
            child._recalc_size()
            child._update_internal_container_on_size()

    @classmethod
    def init_page(
            cls,
            page: ft.Page,
            colour: str = ft.colors.with_opacity(0, "#FFFFFF"),
    ) -> Self:
        """
        Puts an item on the page that expands to fill the page.
        Returns the item.
        """
        root_item = QItem(expand=True, colour=colour)
        root_item._add_to_page(page)
        return root_item
