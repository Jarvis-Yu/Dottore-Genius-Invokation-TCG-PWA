import flet as ft

def make_centre(content: ft.Control) -> ft.Container:
    container = ft.TransparentPointer(
        content=ft.Container(
            content=content,
            alignment=ft.alignment.center,
        ),
    )
    return container