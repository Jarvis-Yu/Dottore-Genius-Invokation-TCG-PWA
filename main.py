import flet as ft
import dgisim

from src.app import DgisimApp


def main(page: ft.Page):
    DgisimApp(page)


ft.app(
    target=main,
    assets_dir="assets",
    view=ft.AppView.FLET_APP,
)
