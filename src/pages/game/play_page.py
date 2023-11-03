from __future__ import annotations
import math
from typing import Any

import flet as ft
import dgisim as ds
from dgisim import support as dssp
from dgisim import summon as dssm
from dgisim import card as dscd
from dgisim.agents import RandomAgent

from ...components.wip import WIP
from ...qcomp import QItem, QAnchor
from ...context import AppContext, GamePlaySettings, PlayerSettings
from ...routes import Route
from ..base import QPage


class GamePlayPage(QPage):
    def post_init(self, context: AppContext) -> None:
        self._context = context
        context.page.bgcolor = context.settings.view_bg_colour
        context.page.navigation_bar.visible = False
        self.add_children((
            game_layer := QItem(
                object_name="game-layer",
                expand=True,
            ),
            menu_layer := QItem(
                object_name="menu-layer",
                expand=True,
            ),
        ))
        self._game_layer = game_layer
        print(self.object_name, f"{self.width=}")
        print(self._game_layer.object_name, f"{self._game_layer.width=}")
        self._menu_layer = menu_layer
        self._menu_layer.add_flet_comp(ft.Row(
            controls=[
                top_right_col_menu := ft.Column(
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                    alignment=ft.MainAxisAlignment.START,
                )
            ],
            expand=True,
        ))
        self._top_right_col_menu = top_right_col_menu

        self._button_exit = ft.IconButton(
            icon=ft.icons.EXIT_TO_APP,
            on_click=self._back_to_home,
            style=context.settings.button_style,
        )
        self._top_right_col_menu.controls.append(self._button_exit)

        # tmp code
        self._home_pid = ds.Pid.P1
        self._example_game_state = ds.GameState.from_default().factory().f_player1(
            lambda p1: p1.factory().f_summons(
                lambda ss: ss.update_summon(
                    dssm.UshiSummon()
                ).update_summon(
                    dssm.OzSummon()
                ).update_summon(
                    dssm.OceanicMimicFrogSummon()
                ).update_summon(
                    dssm.ChainsOfWardingThunderSummon()
                )
            ).f_supports(
                lambda ss: ss.update_support(
                    dssp.LibenSupport(sid=1)
                ).update_support(
                    dssp.LiyueHarborWharfSupport(sid=2)
                ).update_support(
                    dssp.ChangTheNinthSupport(sid=3)
                ).update_support(
                    dssp.PaimonSupport(sid=4)
                )
            ).f_dice(
                lambda _: ds.ActualDice.from_random(8, excepted_elems=set((
                    ds.Element.PYRO,
                    ds.Element.HYDRO,
                    ds.Element.ELECTRO,
                )))
            ).f_hand_cards(
                lambda hcs: ds.Cards({
                    dscd.ProphecyOfSubmersion: 1,
                    dscd.IHaventLostYet: 2,
                    dscd.Starsigns: 1,
                })
            ).build()
        ).f_player2(
            lambda p1: p1.factory().f_summons(
                lambda ss: ss.update_summon(
                    dssm.AutumnWhirlwindSummon()
                ).update_summon(
                    dssm.BakeKurageSummon()
                ).update_summon(
                    dssm.CuileinAnbarSummon()
                ).update_summon(
                    dssm.SesshouSakuraSummon()
                )
            ).f_supports(
                lambda ss: ss.update_support(
                    dssp.NRESupport(sid=1)
                ).update_support(
                    dssp.KnightsOfFavoniusLibrarySupport(sid=2)
                ).update_support(
                    dssp.XudongSupport(sid=3)
                ).update_support(
                    dssp.ParametricTransformerSupport(sid=4)
                )
            ).f_dice(
                lambda _: ds.ActualDice.from_random(8, excepted_elems=set((
                    ds.Element.GEO,
                    ds.Element.ANEMO,
                    ds.Element.CRYO,
                )))
            ).f_hand_cards(
                lambda hcs: ds.Cards({
                    dscd.ElementalResonanceEnduringRock: 1,
                    dscd.SumeruCity: 2,
                    dscd.TheShrinesSacredShade: 1,
                })
            ).build()
        ).build()
        self.rerender()

    def _back_to_home(self, _: Any) -> None:
        self._context.current_route = Route.GAME

    def rerender(self, _: Any = None) -> None:
        self.render_state(self._example_game_state)

    def render_state(self, game_state: ds.GameState) -> None:
        self._top_right_col_menu.controls.clear()
        self._top_right_col_menu.controls.append(self._button_exit)
        self._game_layer.clear()

        self._game_layer.add_children((
            self._card_zone          (0.005, 0.09, ds.Pid.P2, game_state),
            self._support_summon_zone(0.105, 0.09, ds.Pid.P2, game_state),
            self._char_zone          (0.205, 0.21, ds.Pid.P2, game_state),
            self._char_zone          (0.425, 0.21, ds.Pid.P1, game_state),
            self._support_summon_zone(0.645, 0.09, ds.Pid.P1, game_state),
            self._card_zone          (0.745, 0.24, ds.Pid.P1, game_state),
        ))

        return
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

    def _char_zone(
            self, top_pct: float,
            height_pct: float,
            pid: ds.Pid,
            game_state: ds.GameState,
    ) -> QItem:
        item = QItem(
            object_name=f"char-zone-{pid}",
            width_pct=1.0,
            height_pct=height_pct,
            anchor=QAnchor(left=0.0, top=top_pct),
            border=ft.border.all(1, "black"),
        )
        return item

    def _support_summon_zone(
            self, top_pct: float,
            height_pct: float,
            pid: ds.Pid,
            game_state: ds.GameState,
    ) -> QItem:
        item = QItem(
            object_name=f"support-summon-zone-{pid}",
            width_pct=1.0,
            height_pct=height_pct,
            anchor=QAnchor(left=0.0, top=top_pct),
            border=ft.border.all(1, "black"),
        )
        return item

    def _card_zone(
            self, top_pct: float,
            height_pct: float,
            pid: ds.Pid,
            game_state: ds.GameState,
    ) -> QItem:
        item = QItem(
            object_name=f"card-zone-{pid}",
            width_pct=1.0,
            height_pct=height_pct,
            anchor=QAnchor(left=0.0, top=top_pct),
            border=ft.border.all(1, "black"),
        )
        return item

    def character_component(
            self,
            game_state: ds.GameState,
            pid: ds.Pid,
            char: ds.Character,
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
            game_state: ds.GameState,
            pid: ds.Pid,
            support: ds.Support,
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
            game_state: ds.GameState,
            pid: ds.Pid,
            summon: ds.Summon,
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
    ) -> None | ds.GameStateMachine:
        if game_setting.primary_settings.type == "E" and game_setting.oppo_settings.type == "E":
            random_game = ds.GameState.from_default()
            random_game = random_game.factory().mode(ds.mode.AllOmniMode()).build()
            return ds.GameStateMachine(random_game, RandomAgent(), RandomAgent())
        return None
