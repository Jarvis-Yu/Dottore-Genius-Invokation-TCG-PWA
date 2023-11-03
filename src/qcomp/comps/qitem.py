from dataclasses import dataclass
from typing import Sequence

import flet as ft
from typing_extensions import Self

__all__ = [
    "QAlign",
    "QAnchor",
    "QItem",
    "QInset",
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


@dataclass(slots=True)
class QInset:
    left: float | int = 0
    top: float | int = 0
    right: float | int = 0
    bottom: float | int = 0

    @classmethod
    def all(cls, value: float | int) -> Self:
        return cls(value, value, value, value)

    @classmethod
    def horizontal(cls, value: float | int) -> Self:
        return cls(value, 0.0, value, 0.0)

    @classmethod
    def vertical(cls, value: float | int) -> Self:
        return cls(0.0, value, 0.0, value)

    @classmethod
    def hv(cls, horizontal: float | int, vertical: float | int) -> Self:
        return cls(horizontal, vertical, horizontal, vertical)

    def to_flet(self) -> ft.Padding:
        return ft.Padding(self.left, self.top, self.right, self.bottom)


class QItem:
    def __init__(
        self,
        object_name: str = "QItem",
        parent: Self | None = None,
        ref_parent: Self | None = None,
        width: int | None = None,
        height: int | None = None,
        width_pct: float | None = None,
        height_pct: float | None = None,
        width_height_pct: float | None = None,
        height_width_pct: float | None = None,
        expand: bool = False,
        align: QAlign | ft.Alignment | None = None,
        anchor: QAnchor | None = None,
        inset: QInset = QInset.all(0.0),
        clip: ft.ClipBehavior = ft.ClipBehavior.NONE,
        colour: str = ft.colors.with_opacity(0, "#FFFFFF"),
        border: ft.Border | None = None,
        children: Sequence[Self] | Self = (),
        flets: Sequence[ft.Control] | ft.Control = (),
    ):
        self.object_name = object_name
        self.parent = parent
        self.ref_parent = ref_parent if ref_parent is not None else parent
        self.width = width
        self.height = height
        self.width_pct = width_pct
        self.height_pct = height_pct
        self.width_height_pct = width_height_pct
        self.height_width_pct = height_width_pct
        self.expand = expand
        self.align = align if not isinstance(align, QAlign) else align.to_flet()
        self.anchor = anchor
        self.inset = inset if not isinstance(inset, QInset) else inset.to_flet()
        self.clip = clip
        self.colour = colour
        self.border = border
        self.children: list[Self] = list(children) if isinstance(children, Sequence) else [children]
        self.inited = False  # True after _init_by_parent is called

        assert _check_only_one_holds((
            self.anchor is not None,
            self.align is not None,
            self.expand,
        )), "Only one of anchor, align, or expand can be set"

        self._frame = ft.Stack(
            expand=True,
            clip_behavior=self.clip,
        )

        if self.parent is not None:
            self._init_according_to_parent()
        elif self.ref_parent is not None:
            self._init_according_to_ref_parent()

        self.add_flet_comp(flets)

    def _init_by_parent(self, parent: Self) -> None:
        """ Called by parent if this item is added as a child """
        assert self.inited is False
        assert self.parent is None
        self.parent = parent
        self.ref_parent = parent if self.ref_parent is None else self.ref_parent
        self._init_according_to_parent()

    def _init_according_to_parent(self) -> None:
        """ Init this item according to its parent """
        assert self.inited is False
        assert self.parent is not None
        assert self.ref_parent is not None
        self._recalc_size()
        self._init_internal_container()
        self.parent._add_child_item(self)
        self.inited = True
        for child in self.children:
            if child.inited:
                continue
            child._init_by_parent(self)

    def _init_according_to_ref_parent(self) -> None:
        assert self.inited is False
        assert self.parent is None
        assert self.ref_parent is not None
        self._recalc_size()
        self._init_internal_container()
        self.ref_parent._add_ref_child_item(self)
        self.inited = True
        for child in self.children:
            child._init_by_parent(self)

    def _init_internal_container(self) -> None:
        """ Init the internal container """
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
        elif self.parent is not None:
            assert self.ref_parent is not None
            self._container = ft.Container(
                content=self._frame,
                bgcolor=self.colour,
                width=self.width,
                height=self.height,
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
                        left=-self.width / 2 + self.inset.left,
                        top=-self.height / 2 + self.inset.top,
                        right=-self.width / 2 + self.inset.right,
                        bottom=-self.height / 2 + self.inset.bottom,
                    ),
                    alignment=self.align,
                ),
                expand=True,
            )
        else:
            assert self.parent is None
            assert self.ref_parent is not None
            self._container = ft.Container(
                content=self._frame,
                bgcolor=self.colour,
                width=self.width,
                height=self.height,
            )
            self.root_component = ft.TransparentPointer(
                content=self._container,
                width=self.width,
                height=self.height,
            )
        self._container.border = self.border

    def _update_internal_container_on_size(self) -> None:
        """ Update the internal container on size change """
        if self.expand:
            return

        if self.parent is None:
            assert self.ref_parent is not None
            self.root_component.width = self.width
            self.root_component.height = self.height
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
        """ Recalculate or init the size of this item """
        ref_parent_width = self.ref_parent.width if self.ref_parent.width is not None else 0
        ref_parent_height = self.ref_parent.height if self.ref_parent.height is not None else 0

        if self.width_pct is not None:
            self.width = ref_parent_width * self.width_pct
            if self.height_width_pct is not None:
                self.height = self.width * self.height_width_pct
        if self.height_pct is not None:
            self.height = ref_parent_height * self.height_pct
            if self.width_height_pct is not None:
                self.width = self.height * self.width_height_pct

        if self.anchor is not None:
            ref_width = ref_parent_width - self.inset.left - self.inset.right
            ref_height = ref_parent_height - self.inset.top - self.inset.bottom
            if self.anchor.left is not None and self.anchor.right is not None:
                self.width = ref_width * (self.anchor.right - self.anchor.left)
                if self.height_width_pct is not None:
                    self.height = self.width * self.height_width_pct
            if self.anchor.top is not None and self.anchor.bottom is not None:
                self.height = ref_height * (self.anchor.bottom - self.anchor.top)
                if self.width_height_pct is not None:
                    self.width = self.height * self.width_height_pct

            width_pct = self.width / ref_width if ref_width != 0 else 0
            height_pct = self.height / ref_height if ref_height != 0 else 0
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

        if self.expand:
            self.width = ref_parent_width
            self.height = ref_parent_height

        self._on_resized()

    def _add_child_item(self, item: Self) -> None:
        if item not in self.children:
            self.children.append(item)
        if item.root_component not in self._frame.controls:
            self._frame.controls.append(item.root_component)

    def _add_ref_child_item(self, item: Self) -> None:
        if item not in self.children:
            self.children.append(item)

    def clear(self) -> None:
        self._frame.controls.clear()
        self.children.clear()

    def add_children(self, children: Sequence[Self] | Self) -> None:
        children = children if isinstance(children, Sequence) else (children,)
        if self.inited:
            for child in children:
                child._init_by_parent(self)

    def add_flet_comp(self, comp: Sequence[Self] | ft.Control) -> None:
        if isinstance(comp, ft.Control):
            self._frame.controls.append(comp)
        else:
            self._frame.controls.extend(comp)

    def _add_to_page(self, page: ft.Page) -> None:
        self.width = page.width - page.padding * 2
        self.height = page.height - page.padding * 2
        self._init_internal_container()
        page.bgcolor = self.colour
        page.controls.append(ft.SafeArea(
            content=self.root_component,
            expand=True,
        ))

        def on_resize(_: ft.ControlEvent) -> None:
            self.width = page.width - page.padding * 2
            self.height = page.height - page.padding * 2
            self._on_resized()
            page.update()

        page.on_resize = on_resize

    def _on_resized(self) -> None:
        for child in self.children:
            if not child.inited:
                continue
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
        root_item.inited = True
        return root_item
