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
from ...components.centre import make_centre
from ...qcomp import QItem, QAnchor, QAlign
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
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().active_character_id(
                    2
                ).f_character(
                    1,
                    lambda c: c.factory().energy(
                        2
                    ).elemental_aura(
                        ds.ElementalAura.from_default().add(ds.Element.HYDRO),
                    ).build()
                ).f_character(
                    2,
                    lambda c: c.factory().elemental_aura(
                        ds.ElementalAura.from_default().add(ds.Element.ELECTRO),
                    ).build()
                ).build()
            ).f_summons(
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
            lambda p2: p2.factory().f_characters(
                lambda cs: cs.factory().active_character_id(
                    3
                ).f_character(
                    1,
                    lambda c: c.factory().elemental_aura(
                        ds.ElementalAura.from_default().add(ds.Element.PYRO),
                    ).build()
                ).f_character(
                    2,
                    lambda c: c.factory().energy(
                        1
                    ).elemental_aura(
                        ds.ElementalAura.from_default().add(
                            ds.Element.DENDRO
                        ).add(
                            ds.Element.CRYO
                        ),
                    ).build()
                ).f_character(
                    3,
                    lambda c: c.factory().energy(1).build()
                ).build()
            ).f_summons(
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
            self._card_zone(0.005, 0.09, ds.Pid.P2, game_state),
            self._support_summon_zone(0.105, 0.09, ds.Pid.P2, game_state),
            self._char_zone(0.205, 0.22, ds.Pid.P2, game_state),
            self._char_zone(0.435, 0.22, ds.Pid.P1, game_state),
            self._support_summon_zone(0.665, 0.09, ds.Pid.P1, game_state),
            self._card_zone(0.765, 0.22, ds.Pid.P1, game_state),
        ))

        return

    def _char_zone(
            self,
            top_pct: float,
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
        chars = game_state.get_player(pid).get_characters()
        item.add_flet_comp(ft.Row(
            controls=[
                self._character(item, pid, char.get_id(), game_state).root_component
                for char in chars
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        ))
        return item

    def _support_summon_zone(
            self,
            top_pct: float,
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
            self,
            top_pct: float,
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

    def _character(
            self,
            ref_parent: QItem,
            pid: ds.Pid,
            char_id: int,
            game_state: ds.GameState,
    ) -> QItem:
        chars = game_state.get_player(pid).get_characters()
        char = chars.just_get_character(char_id)
        is_active = char.get_id() == chars.just_get_active_character_id()
        inactive_top, active_top = (0.1, 0.0) if pid is self._home_pid else (0.0, 0.1)
        item = QItem(
            object_name=f"char-{pid}-{char_id}-{char.name()}",
            ref_parent=ref_parent,
            height_pct=1.0,
            width_height_pct=0.65,
            # border=ft.border.all(1, "black"),
            children=(
                char_item := QItem(
                    object_name=f"char-{pid}-{char_id}-{char.name()}-body",
                    height_pct=0.9,
                    anchor=QAnchor(
                        left=0.0,
                        right=1.0,
                        top=active_top if is_active else inactive_top,
                    ),
                    border=ft.border.all(1, "red"),
                    children=(
                        aura_bar := QItem(
                            object_name=f"char-{pid}-{char_id}-{char.name()}-aura-bar",
                            height_pct=0.14,
                            width_pct=0.6,
                            anchor=QAnchor(left=0.2, top=0.0),
                        ),
                        char_card := QItem(
                            object_name=f"char-{pid}-{char_id}-{char.name()}-card",
                            height_pct=0.7,
                            width_height_pct=0.75,
                            align=QAlign(x_pct=0.5, y_pct=0.52),
                            border=ft.border.all(1, "blue"),
                        ),
                    ),
                ),
            ),
        )
        char_card.add_flet_comp(
            make_centre(ft.Text(char.name()))
        )
        char_card.add_children((
            hp_item := QItem(
                object_name=f"char-{pid}-{char_id}-{char.name()}-health",
                height_pct=0.25,
                width_height_pct=1.0,
                align=QAlign(x_pct=0.0, y_pct=0.0),
                colour="#A87845",
                border=ft.border.all(1, "green"),
            ),
        ))
        hp_item.add_flet_comp((
            make_centre(ft.Text(f"{char.get_hp()}"))
        ))
        energy_height = 0.13
        for energy in range(1, char.get_max_energy() + 1):
            char_card.add_children((
                QItem(
                    height_pct=energy_height,
                    width_height_pct=1.0,
                    align=QAlign(x_pct=1.0, y_pct=(2 * energy - 1) * energy_height),
                    colour=ft.colors.with_opacity(
                        1 if energy <= char.get_energy() else 0.2, "yellow"
                    ),
                )
            ))
        elem_colour_map = {
            ds.Element.PYRO: "#E9683E",
            ds.Element.HYDRO: "#4CBBEA",
            ds.Element.ANEMO: "#6CBE9F",
            ds.Element.ELECTRO: "#A57FB6",
            ds.Element.DENDRO: "#9AC546",
            ds.Element.CRYO: "#96D1DC",
            ds.Element.GEO: "#F6AD43",
        }
        elem_name_map = {
            ds.Element.PYRO: "pyro",
            ds.Element.HYDRO: "hydro",
            ds.Element.ANEMO: "anemo",
            ds.Element.ELECTRO: "electro",
            ds.Element.DENDRO: "dendro",
            ds.Element.CRYO: "cryo",
            ds.Element.GEO: "geo",
        }
        aura_bar.add_flet_comp(
            aura_row := ft.Row(
                controls=[
                    (
                        elem_frame := QItem(
                            ref_parent=aura_bar,
                            height_pct=1.0,
                            width_height_pct=1.0,
                        ),
                        elem_frame.add_flet_comp(
                            ft.Image(
                                src=f"assets/elem_icons/{elem_name_map[elem]}.png",
                                fit=ft.ImageFit.FILL,
                            )
                        )
                    )[0].root_component
                    for elem in char.get_elemental_aura()
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            )
        )
        return item
