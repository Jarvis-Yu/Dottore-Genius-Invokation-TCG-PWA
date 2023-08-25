import flet as ft

from ..context import AppContext

class WIP(ft.Container):
    def __init__(self, context: AppContext, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alignment = ft.alignment.center
        self.content = ft.Text(
            value="WIP",
            color=context.settings.normal_text_colour,
            size=50,
            italic=True,
        )