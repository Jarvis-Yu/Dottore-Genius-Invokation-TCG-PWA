"""
Copyright (C) 2024 Leyang Yu

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
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