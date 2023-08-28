import flet as ft

from ..context import AppContext

class WIP(ft.TransparentPointer):
    def __init__(self, context: AppContext, *args, **kwargs):
        self._container = ft.Container(*args, **kwargs)
        super().__init__(content=self._container)
        self._container.alignment = ft.alignment.center
        self._container.content = ft.Text(
            value="WIP",
            color=context.settings.normal_text_colour,
            size=50,
            italic=True,
        )