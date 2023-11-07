import flet as ft

from .qitem import QItem

__all__ = ["QText"]

class QText(QItem):
    def __init__(
            self,
            text: str = "",
            text_colour: str | None = None,
            text_alignment: ft.alignment = ft.alignment.center,
            size_rel_height: float | None = None,
            size_rel_width: float | None = None,
            size: float | int | None = None,
            **kwargs,
        ):
            self._size_rel_height = size_rel_height
            self._size_rel_width = size_rel_width
            self._text = ft.Text(value=text, size=size, color=text_colour)
            super().__init__(**kwargs)
            self.add_flet_comp(ft.TransparentPointer(
                content=ft.Container(
                    content=self._text,
                    alignment=text_alignment,
                ),
            ))

    def _on_resized(self) -> None:
        if self._size_rel_height is not None:
            self._text.size = self.height * self._size_rel_height
        elif self._size_rel_width is not None:
            self._text.size = self.width * self._size_rel_width
        super()._on_resized()