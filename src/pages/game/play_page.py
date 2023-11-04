from __future__ import annotations
from math import pi
from typing import Any

import flet as ft
import dgisim as ds
from dgisim import card as dscd
from dgisim import status as dsst
from dgisim import summon as dssm
from dgisim import support as dssp
from dgisim.agents import RandomAgent

from ...components.wip import WIP
from ...components.centre import make_centre
from ...qcomp import QItem, QAnchor, QAlign, QImage
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
                    ).f_equipments(
                        lambda es: es.update_status(
                            dsst.GamblersEarringsStatus()
                        ).update_status(
                            dsst.AmosBowStatus()
                        )
                    ).build()
                ).f_character(
                    2,
                    lambda c: c.factory().elemental_aura(
                        ds.ElementalAura.from_default().add(ds.Element.ELECTRO),
                    ).f_equipments(
                        lambda es: es.update_status(
                            dsst.AmosBowStatus()
                        ).update_status(
                            dsst.ColdBloodedStrikeStatus()
                        ).update_status(
                            dsst.GamblersEarringsStatus()
                        )
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
                lambda _: ds.ActualDice.from_random(16, excepted_elems=set((
                    ds.Element.PYRO,
                    ds.Element.HYDRO,
                    ds.Element.ELECTRO,
                )))
            ).f_hand_cards(
                lambda hcs: ds.Cards({
                    dscd.ProphecyOfSubmersion: 1,
                    dscd.IHaventLostYet: 2,
                    dscd.Starsigns: 1,
                    dscd.ElementalResonanceWovenThunder: 2,
                    dscd.LiyueHarborWharf: 2,
                    dscd.LeaveItToMe: 2,
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
                    lambda c: c.factory().energy(
                        1
                    ).f_equipments(
                        lambda es: es.update_status(
                            dsst.GamblersEarringsStatus()
                        ).update_status(
                            dsst.ColdBloodedStrikeStatus()
                        )
                    ).build()
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
        ).build().prespective_view(self._home_pid)
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

    dssm.AutumnWhirlwindSummon

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
            children=(
                self._support_zone(pid, game_state),
                self._summon_zone(pid, game_state),
            ),
        )
        return item

    def _support_zone(
            self,
            pid: ds.Pid,
            game_state: ds.GameState,
    ) -> QItem:
        item = QItem(
            object_name=f"support-zone-{pid}",
            width_pct=0.5,
            height_pct=1.0,
            anchor=QAnchor(left=0.0, top=0.0),
            children=([
                QItem(
                    width_pct=0.22,
                    height_pct=1.0,
                    anchor=QAnchor(left=i * 0.25 + 0.02, top=0.0),
                    colour="#A87845",
                    children=(
                        self._support(support, pid, game_state),
                    ),
                )
                for i, support in enumerate(game_state.get_player(pid).get_supports())
            ]),
        )
        return item

    def _summon_zone(
            self,
            pid: ds.Pid,
            game_state: ds.GameState,
    ) -> QItem:
        item = QItem(
            object_name=f"summon-zone-{pid}",
            width_pct=0.5,
            height_pct=1.0,
            anchor=QAnchor(left=0.5, top=0.0),
            children=([
                QItem(
                    width_pct=0.22,
                    height_pct=1.0,
                    anchor=QAnchor(left=i * 0.25 + 0.02, top=0.0),
                    colour="#A87845",
                    children=(
                        self._summon(summon, pid, game_state),
                    ),
                )
                for i, summon in enumerate(game_state.get_player(pid).get_summons())
            ]),
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
            children=(
                self._cards(pid, game_state),
                self._dice(pid, game_state),
            ),
        )
        return item

    def _support(
            self,
            support: ds.Support,
            pid: ds.Pid,
            game_state: ds.GameState,
    ) -> QItem:
        item = QItem(
            expand=True,
            children=(
                QImage(
                    object_name="support-img",
                    src=f"assets/supports/{support.__class__.__name__}.png",
                    expand=True,
                ),
            ),
            flets=[
                ft.Text(f"{support.__class__.__name__}"),
            ]
        )
        if hasattr(support, "usages"):
            item.add_children((
                QItem(
                    object_name="support-count-down",
                    height_pct=0.2,
                    width_height_pct=1.0,
                    align=QAlign(x_pct=0.95, y_pct=0.05),
                    colour="#887054",
                    border=ft.border.all(1, "#DBC9AF"),
                    flets=(
                        make_centre(ft.Text(
                            value=f"{support.usages}",
                            color="#FFFFFF",
                            size=9,
                        )),
                    ),
                ),
            ))
        return item

    def _summon(
            self,
            summon: ds.Summon,
            pid: ds.Pid,
            game_state: ds.GameState,
    ) -> QItem:
        item = QItem(
            expand=True,
            children=(
                QImage(
                    object_name="summon-img",
                    src=f"assets/summons/{summon.__class__.__name__}.png",
                    expand=True,
                ),
                QItem(
                    object_name="summon-count-down",
                    height_pct=0.2,
                    width_height_pct=1.0,
                    align=QAlign(x_pct=0.95, y_pct=0.05),
                    colour="#887054",
                    border=ft.border.all(1, "#DBC9AF"),
                    flets=(
                        make_centre(ft.Text(
                            value=f"{summon.usages}",
                            color="#FFFFFF",
                            size=9,
                        )),
                    ),
                ),
            ),
            flets=(
                ft.Text(f"{summon.__class__.__name__}"),
            ),
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
            children=(
                char_item := QItem(
                    object_name=f"char-{pid}-{char_id}-{char.name()}-body",
                    height_pct=0.9,
                    anchor=QAnchor(
                        left=0.0,
                        right=1.0,
                        top=active_top if is_active else inactive_top,
                    ),
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
                            border=ft.border.all(1, "#DBC9AF"),
                        ),
                    ),
                ),
            ),
        )
        char_card.add_flet_comp((
            make_centre(ft.Text(char.name())),
            ft.Image(
                src=f"assets/char_cards/{char.name()}75.png",
                fit=ft.ImageFit.FILL,
            ),
        ))
        char_card.add_children((
            hp_item := QItem(
                object_name=f"char-{pid}-{char_id}-{char.name()}-health",
                height_pct=0.2,
                width_height_pct=1.0,
                align=QAlign(x_pct=0.0, y_pct=0.0),
                colour="#A87845",
                border=ft.border.all(2, "#DBC9AF"),
                rotate=ft.Rotate(angle=0.25*pi, alignment=ft.alignment.center),
            ),
            equip_item := QItem(
                object_name=f"char-{pid}-{char_id}-{char.name()}-equip",
                height_pct=0.8,
                width_pct=0.2,
                anchor=QAnchor(left=-0.1, top=0.2),
            ),
        ))
        hp_item.add_children(
            QItem(
                height_pct=1.0,
                width_pct=2.0,
                align=QAlign(x_pct=0.5, y_pct=0.5),
                rotate=ft.Rotate(angle=-0.25*pi, alignment=ft.alignment.center),
                flets=(
                    make_centre(ft.Text(f"{char.get_hp()}")),
                ),
            ),
        )
        equipments: ds.EquipmentStatuses = char.get_equipment_statuses()
        eq_map = {
            dsst.TalentEquipmentStatus: "Talent",
            dsst.EquipmentStatus: "Weapon",
            dsst.ArtifactEquipmentStatus: "Artifact",
        }
        eqs: list[str] = []
        for eq_type, name in eq_map.items():
            if equipments.find_type(eq_type):
                eqs.append(name)
        equip_item.add_children([
            QItem(
                width_pct=1.0,
                height_width_pct=1.0,
                anchor=QAnchor(left=0.0, top=i * 0.225),
                children=(
                    QImage(
                        src=f"assets/icons/{eq_name}Icon.png",
                        expand=True,
                    ),
                ),
            )
            for i, eq_name in enumerate(eqs)
        ])

        energy_height = 0.13
        for energy in range(1, char.get_max_energy() + 1):
            char_card.add_children((
                QItem(
                    height_pct=energy_height,
                    width_height_pct=1.0,
                    align=QAlign(x_pct=1.0, y_pct=(1.5 * energy - 0.5) * energy_height),
                    colour=ft.colors.with_opacity(
                        1, "#EEEE00" if energy <= char.get_energy() else "#A28E75"
                    ),
                    border=ft.border.all(2, "#DBC9AF"),
                    rotate=ft.Rotate(angle=0.25*pi, alignment=ft.alignment.center),
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

    def _dice(
            self,
            pid: ds.Pid,
            game_state: ds.GameState,
    ) -> QItem:
        elem_die_map = {
            ds.Element.PYRO: "Pyro",
            ds.Element.HYDRO: "Hydro",
            ds.Element.ANEMO: "Anemo",
            ds.Element.ELECTRO: "Electro",
            ds.Element.DENDRO: "Dendro",
            ds.Element.CRYO: "Cryo",
            ds.Element.GEO: "Geo",
            ds.Element.OMNI: "Omni",
            ds.Element.ANY: "Any",
        }
        dice = game_state.get_player(pid).get_dice()
        if pid is self._home_pid:
            die_list: list[ds.Element] = []
            for elem, num in dice.readonly_dice_ordered(game_state.get_player(pid)).items():
                die_list.extend([elem] * num)
            item = QItem(
                expand=True,
                children=(
                    dice_row_item := QItem(
                        height_pct=0.12,
                        width_pct=1.0,
                        anchor=QAnchor(left=0.0, top=0.0),
                    ),
                    deck_corner := QItem(
                        height_pct=1.0 / 22 * 9,
                        width_height_pct=7 / 12,
                        anchor=QAnchor(left=0.0, bottom=1.0),
                        colour="#000000",
                        children=(
                            QImage(
                                src=f"assets/cards/OmniCardCard.png",
                                expand=True,
                            ),
                            QItem(
                                expand=True,
                                colour=ft.colors.with_opacity(0.2, "#000000"),
                                flets=(
                                    make_centre(ft.Text(
                                        f"{game_state.get_player(pid).get_deck_cards().num_cards()}"
                                    )),
                                ),
                            ),
                        ),
                    ),
                ),
            )
            dice_row_item.add_flet_comp((
                ft.Row(
                    controls=[
                        QItem(
                            ref_parent=dice_row_item,
                            height_pct=1.0,
                            width_height_pct=1.0,
                            children=(
                                QImage(
                                    src=f"assets/dice/{elem_die_map[elem]}Die.png",
                                    expand=True,
                                ),
                            ),
                        ).root_component
                        for elem in die_list
                    ],
                    spacing=1,
                    expand=True,
                ),
            ))
        else:
            item = QItem(
                expand=True,
                children=(
                    QItem(
                        anchor=QAnchor(left=0.0, right=1.0, top=-0.1, bottom=0.9),
                        flets=(
                            info_row := ft.Row(
                                controls=[],
                                alignment=ft.MainAxisAlignment.START,
                            ),
                        ),
                    ),
                ),
            )
            dice_info = QItem(
                ref_parent=item,
                height_pct=0.5,
                width_height_pct=1.0,
                children=(
                    QImage(
                        src=f"assets/dice/{elem_die_map[ds.Element.ANY]}Die.png",
                        expand=True,
                    ),
                    QItem(
                        expand=True,
                        flets=(
                            make_centre(ft.Text(f"{dice.num_dice()}")),
                        ),
                    ),
                )
            )
            card_info = QItem(
                ref_parent=item,
                height_pct=1.0,
                width_height_pct=7 / 12,
                colour="#000000",
                children=(
                    QImage(
                        src=f"assets/cards/OmniCardCard.png",
                        expand=True,
                    ),
                    QItem(
                        expand=True,
                        colour=ft.colors.with_opacity(0.2, "#000000"),
                        flets=(
                            make_centre(ft.Text(
                                f"{game_state.get_player(pid).get_deck_cards().num_cards()}"
                            )),
                        ),
                    ),
                ),
            )
            info_row.controls.extend((
                card_info.root_component,
                dice_info.root_component,
            ))
        return item

    def _cards(
            self,
            pid: ds.Pid,
            game_state: ds.GameState,
    ) -> QItem:
        cards = game_state.get_player(pid).get_hand_cards()
        card_list: list[type[ds.Card]] = []
        for card in cards:
            for _ in range(cards[card]):
                card_list.append(card)

        if pid is self._home_pid:
            item = QItem(
                object_name=f"cards-{pid}",
                width_pct=1.0,
                height_pct=1.0,
                anchor=QAnchor(left=0.0, top=0.3),
                children=[
                    self._card(i, card, pid, game_state)
                    for i, card in enumerate(card_list)
                ],
            )
        else:
            item = QItem(
                object_name=f"cards-{pid}",
                width_pct=1.0,
                height_pct=0.22 / 0.09,
                anchor=QAnchor(left=0.0, bottom=1.0),
                children=[
                    self._card(i, card, pid, game_state)
                    for i, card in enumerate(card_list)
                ],
            )
        return item

    def _card(
            self,
            idx: int,
            card: ds.Card,
            pid: ds.Pid,
            game_state: ds.GameState,
    ) -> QItem:
        item = QItem(
            height_pct=1.0,
            width_height_pct=7 / 12,
            anchor=QAnchor(left=idx * 0.08, top=0.0),
            children=(
                QItem(
                    width_pct=0.9,
                    height_pct=0.9,
                    align=QAlign(x_pct=0.5, y_pct=0.5),
                    colour="#A87845",
                    border=ft.border.all(1, "black"),
                    flets=(
                        make_centre(ft.Text(card.name())),
                    )
                ),
                QImage(
                    src=f"assets/cards/{card.name()}Card.png",
                    expand=True,
                ),
            ),
        )
        return item
