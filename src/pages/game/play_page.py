from __future__ import annotations
import math
from typing import Any

import flet as ft
import dgisim as dm
from dgisim.agents import RandomAgent

from ...components.wip import WIP
from ...qcomp import QItem
from ...context import AppContext, GamePlaySettings, PlayerSettings
from ...routes import Route


class GamePlayPage(ft.Stack):
    def __init__(self, context: AppContext, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._context = context
        context.page.bgcolor = context.settings.view_bg_colour
        context.page.navigation_bar.visible = False
        self.expand = True
        self._game_content = ft.Stack(expand=True)
        self._menu_content = ft.Stack(expand=True)
        self.controls.append(ft.TransparentPointer(ft.Container(
            content=self._game_content,
            padding=10,
        )))
        self.controls.append(ft.TransparentPointer(ft.Container(
            content=self._menu_content,
            padding=10,
        )))

        self._game_state_machine = self.build_game_state_machine_from_mode(context.game_mode)

        if self._game_state_machine == None:
            self.controls.append(WIP(context))
            self._game_content.controls.append(
                ft.TransparentPointer(ft.Container(
                    content=ft.IconButton(
                        icon=ft.icons.EXIT_TO_APP,
                        on_click=self._back_to_home,
                        style=context.settings.button_style,
                    ),
                    alignment=ft.alignment.top_right,
                ))
            )
            return

        self._game_state_machine.step_until_phase(
            self._game_state_machine.get_game_state().get_mode().action_phase)

        self._curr_home_pid = self._context.game_mode.primary_player
        self._context.on_reference_size_changed.add(self.rerender)

    def _back_to_home(self, _: Any) -> None:
        self._context.current_route = Route.GAME

    def rerender(self, _: Any = None) -> None:
        self.render_state(self._game_state_machine.get_game_state())

    def render_state(self, game_state: dm.GameState) -> None:
        self._game_content.controls.clear()
        self._menu_content.controls.clear()

        # menu
        menu_col = ft.Column()
        self._menu_content.controls.append(
            ft.TransparentPointer(ft.Container(
                content=menu_col,
                alignment=ft.alignment.top_right
            ))
        )
        menu_col.controls.append(
            ft.IconButton(
                icon=ft.icons.EXIT_TO_APP,
                on_click=self._back_to_home,
                style=self._context.settings.button_style,
            )
        )

        def step_game(_: Any) -> None:
            self._game_state_machine.auto_step()
            self._game_state_machine.one_step()
            self._game_state_machine.auto_step()
            self.render_state(self._game_state_machine.get_game_state())
            self.update()

        menu_col.controls.append(
            ft.IconButton(
                icon=ft.icons.HOURGLASS_BOTTOM,
                on_click=step_game,
                style=self._context.settings.button_style,
            )
        )

        # zones
        oppo_card_zone = ft.TransparentPointer(ft.Container(
            content=ft.Text("oppo_card_zone"),
            bgcolor=self._context.settings.nav_bar_colour,
            border=ft.border.all(1, "black"),
            alignment=ft.alignment.center,
            height=self._context.reference_size.y * 0.1,
        ))
        oppo_support_summon_zone = ft.TransparentPointer(ft.Container(
            content=ft.Text("oppo_support_summon_zone"),
            bgcolor=self._context.settings.nav_bar_colour,
            border=ft.border.all(1, "black"),
            alignment=ft.alignment.center,
            height=self._context.reference_size.y * 0.07,
        ))
        oppo_chars_zone = ft.TransparentPointer(ft.Container(
            content=ft.Text("oppo_chars_zone"),
            bgcolor=self._context.settings.nav_bar_colour,
            border=ft.border.all(1, "black"),
            alignment=ft.alignment.center,
            height=self._context.reference_size.y * 0.21,
        ))
        self_chars_zone = ft.TransparentPointer(ft.Container(
            content=ft.Text("self_chars_zone"),
            bgcolor=self._context.settings.nav_bar_colour,
            border=ft.border.all(1, "black"),
            alignment=ft.alignment.center,
            height=self._context.reference_size.y * 0.21,
        ))
        self_support_summon_zone = ft.TransparentPointer(ft.Container(
            content=ft.Text("self_support_summon_zone"),
            bgcolor=self._context.settings.nav_bar_colour,
            border=ft.border.all(1, "black"),
            alignment=ft.alignment.center,
            height=self._context.reference_size.y * 0.07,
        ))
        self_card_zone = ft.TransparentPointer(ft.Container(
            content=ft.Text("self_card_zone"),
            bgcolor=self._context.settings.nav_bar_colour,
            border=ft.border.all(1, "black"),
            alignment=ft.alignment.center,
            height=self._context.reference_size.y * 0.2,
        ))

        zone_col = ft.Column(
            controls=[
                oppo_card_zone,
                oppo_support_summon_zone,
                oppo_chars_zone,
                self_chars_zone,
                self_support_summon_zone,
                self_card_zone,
            ],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        )

        self._game_content.controls.append(zone_col)

        # fill data
        half_width = (self._context.page.width - 20) / 2

        self_player = game_state.get_player(self._curr_home_pid)
        self_chars = self_player.get_characters()
        self_char_row = ft.Row(
            controls=[
                self.character_component(game_state, self._curr_home_pid, char)
                for char in self_chars
            ],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        )
        self_chars_zone.content.content = self_char_row
        self_supports = self_player.get_supports()
        self_support_row = ft.Row(
            controls=[
                self.support_component(game_state, self._curr_home_pid, support)
                for support in self_supports
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self_summons = self_player.get_summons()
        self_summon_row = ft.Row(
            controls=[
                self.summon_component(game_state, self._curr_home_pid, summon)
                for summon in self_summons
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self_support_summon_zone.content.content = ft.Stack(
            controls=[
                ft.TransparentPointer(ft.Container(
                    content=self_support_row,
                    alignment=ft.alignment.center_left,
                ), left=0),
                ft.TransparentPointer(ft.Container(
                    content=self_summon_row,
                    alignment=ft.alignment.center_left,
                ), left=half_width),
            ]
        )

        oppo_player = game_state.get_player(self._curr_home_pid.other())
        oppo_chars = oppo_player.get_characters()
        oppo_char_row = ft.Row(
            controls=[
                self.character_component(game_state, self._curr_home_pid.other(), char)
                for char in oppo_chars
            ],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        )
        oppo_chars_zone.content.content = oppo_char_row
        oppo_supports = oppo_player.get_supports()
        oppo_support_row = ft.Row(
            controls=[
                self.support_component(game_state, self._curr_home_pid.other(), support)
                for support in oppo_supports
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        oppo_summons = oppo_player.get_summons()
        oppo_summon_row = ft.Row(
            controls=[
                self.summon_component(game_state, self._curr_home_pid.other(), summon)
                for summon in oppo_summons
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        oppo_support_summon_zone.content.content = ft.Stack(
            controls=[
                ft.TransparentPointer(ft.Container(
                    content=oppo_support_row,
                    alignment=ft.alignment.center_left,
                ), left=0),
                ft.TransparentPointer(ft.Container(
                    content=oppo_summon_row,
                    alignment=ft.alignment.center_left,
                ), left=half_width),
            ]
        )

    def character_component(
            self,
            game_state: dm.GameState,
            pid: dm.Pid,
            char: dm.Character,
    ) -> ft.TransparentPointer:
        max_height: float = self._context.reference_size.y * 0.21
        base_stack = ft.Stack(clip_behavior=ft.ClipBehavior.NONE)
        base = ft.Container(
            content=base_stack,  # ft.Text(char.name(), color="black"),
            border=ft.border.all(1, color="black"),
            alignment=ft.alignment.center,
            width=max_height * 0.55,
            height=max_height * 0.8,
            offset=(
                ft.transform.Offset(0, -0.1 if pid is self._curr_home_pid else 0.1)
                if char.get_id() == game_state.get_player(pid).get_characters().get_active_character_id()
                else ft.transform.Offset(0, 0)
            ),
        )
        card = ft.TransparentPointer(ft.Container(
            content=ft.Text(char.name(), color="black"),
            alignment=ft.alignment.center,
            bgcolor="white",
            width=max_height * 0.4,
            height=max_height * 0.6,
        ))
        hp = ft.TransparentPointer(ft.Container(
            content=ft.Text(str(char.get_hp()), size=max_height * 0.07),
            alignment=ft.alignment.center,
            bgcolor="red",
            border_radius=max_height,
            width=max_height * 0.15,
            height=max_height * 0.15,
        ))
        energy = ft.TransparentPointer(ft.Container(
            content=ft.Column(
                controls=[
                    ft.TransparentPointer(ft.Container(
                        bgcolor=ft.colors.with_opacity(
                            1 if i < char.get_energy() else 0.2, "yellow"),
                        border=ft.border.all(1, color="yellow"),
                        rotate=ft.transform.Rotate(math.pi / 4, alignment=ft.alignment.center),
                        width=max_height * 0.07,
                        height=max_height * 0.07,
                    ))
                    for i in range(char.get_max_energy())
                ],
                spacing=max_height * 0.05,
            ),
            alignment=ft.alignment.top_center,
        ))
        base_stack.controls.append(ft.TransparentPointer(ft.Container(
            content=card,
            alignment=ft.alignment.center,
        )))
        base_stack.controls.append(ft.TransparentPointer(ft.Container(
            content=hp,
        ), top=max_height * 0.025))
        base_stack.controls.append(ft.TransparentPointer(ft.Container(
            content=energy,
        ), top=max_height * 0.13, right=max_height * 0.037))
        return ft.TransparentPointer(base)

    def support_component(
            self,
            game_state: dm.GameState,
            pid: dm.Pid,
            support: dm.Support,
    ) -> ft.TransparentPointer:
        max_height: float = self._context.reference_size.y * 0.07
        max_width: float = (self._context.reference_size.x - 100) / 8
        max_size = min(max_height, max_width)
        base_stack = ft.Stack(clip_behavior=ft.ClipBehavior.NONE)
        base = ft.Container(
            content=base_stack,
            bgcolor="white",
            width=max_width,
            height=max_height,
        )
        name = ft.Text(
            value=f"{support.__class__.__name__}",
            color="black",
            size=max_size / 7,
        )
        base_stack.controls.append(ft.TransparentPointer(ft.Container(
            content=name,
            alignment=ft.alignment.center,
        )))
        return ft.TransparentPointer(base)

    def summon_component(
            self,
            game_state: dm.GameState,
            pid: dm.Pid,
            summon: dm.Summon,
    ) -> ft.TransparentPointer:
        max_height: float = self._context.reference_size.y * 0.07
        max_width: float = (self._context.reference_size.x - 100) / 8
        max_size = min(max_height, max_width)
        base_stack = ft.Stack(clip_behavior=ft.ClipBehavior.NONE)
        base = ft.Container(
            content=base_stack,
            bgcolor="white",
            width=max_width,
            height=max_height,
        )
        name = ft.Text(
            value=f"{summon.__class__.__name__}({summon.usages})",
            color="black",
            size=max_size / 7,
        )
        base_stack.controls.append(ft.TransparentPointer(ft.Container(
            content=name,
            alignment=ft.alignment.center,
        )))
        return ft.TransparentPointer(base)

    def build_game_state_machine_from_mode(
            self, game_setting: GamePlaySettings
    ) -> None | dm.GameStateMachine:
        if game_setting.primary_settings.type == "E" and game_setting.oppo_settings.type == "E":
            random_game = dm.GameState.from_default()
            random_game = random_game.factory().mode(dm.mode.AllOmniMode()).build()
            return dm.GameStateMachine(random_game, RandomAgent(), RandomAgent())
        return None
