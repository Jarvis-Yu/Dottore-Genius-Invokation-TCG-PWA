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

from .qitem import QItem

__all__ = ["QImage"]

class QImage(QItem):
    def __init__(
            self,
            src: str = "",
            border_radius: float | int | None = None,
            fit: ft.ImageFit = ft.ImageFit.COVER,
            **kwargs,
        ):
        self._image = ft.Image(src=src, border_radius=border_radius, fit=fit)
        super().__init__(border_radius=border_radius, **kwargs)
        self._image.width = self.width
        self._image.height = self.height
        self.add_flet_comp(self._image)
    
    def _on_resized(self) -> None:
        self._image.width = self.width
        self._image.height = self.height
        super()._on_resized()
