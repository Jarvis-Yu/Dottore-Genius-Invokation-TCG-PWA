from __future__ import annotations
from collections import defaultdict
from math import pi
from typing import Any, Callable, cast

import flet as ft
import dgisim as ds
from dgisim import card as dscd
from dgisim import status as dsst
from dgisim import summon as dssm
from dgisim import support as dssp
from dgisim.agents import RandomAgent

from ...components.wip import WIP
from ...components.centre import make_centre
from ...qcomp import QItem, QAnchor, QAlign, QImage, QText
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
            info_layer := QItem(
                object_name="info-layer",
                expand=True,
            ),
            prompt_action_layer := QItem(
                object_name="prompt-action-layer",
                expand=True,
            )
        ))
        self._game_layer = game_layer
        self._menu_layer = menu_layer
        self._info_layer = info_layer
        self._prompt_action_layer = prompt_action_layer

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

        self._home_pid = ds.Pid.P1
        self.rerender()

    def _back_to_home(self, _: Any) -> None:
        self._context.current_route = Route.GAME

    def submit_action(self, action: ds.PlayerAction) -> None:
        self._act_gen = []
        self._context.game_data.take_action(self._home_pid, action)
        self.rerender()
        self.root_component.update()

    def rerender(self, _: Any = None) -> None:
        self._curr_state = self._context.game_data.curr_game_state(self._home_pid)
        self._act_gen: list[ds.ActionGenerator] | None = None
        if self._curr_state.waiting_for() is self._home_pid:
            self._act_gen = [self._curr_state.action_generator(self._home_pid)]
        self.render_prompt_action()
        self.render_state(self._curr_state)

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

    def render_prompt_action(self) -> None:
        self._prompt_action_layer.clear()
        if self._act_gen is None:
            return
        if len(self._act_gen) == 1:
            mode = self._curr_state.get_mode()
            print("matching", type(self._curr_state.get_phase()))
            match type(self._curr_state.get_phase()):
                case mode.card_select_phase:
                    choices = self._act_gen[0].choices()
                    if ds.ActionType.SELECT_CARDS in choices:
                        self._show_select_cards([
                            self._act_gen[0],
                            self._act_gen[0].choose(ds.ActionType.SELECT_CARDS),
                        ])
                case mode.starting_hand_select_phase:
                    choices = self._act_gen[0].choices()
                    self._show_select_chars(self._act_gen)
                case mode.roll_phase:
                    choices = self._act_gen[0].choices()
                    if ds.ActionType.SELECT_DICE in choices:
                        self._show_select_dice([
                            self._act_gen[0],
                            self._act_gen[0].choose(ds.ActionType.SELECT_DICE),
                        ])
                    else:
                        self.submit_action(ds.EndRoundAction())

    def _show_select_cards(self, pres: list[ds.ActionGenerator]) -> None:
        choices = pres[-1].choices()
        assert isinstance(choices, ds.Cards)
        self._prompt_action_layer.clear()
        self._prompt_action_layer.add_children((
            background := QItem(
                object_name="click_cover",
                expand=True,
                colour=ft.colors.with_opacity(0.5, "#000000"),
            ),
        ))
        background.add_flet_comp(ft.GestureDetector(
            on_tap=lambda _: None,
            mouse_cursor=ft.MouseCursor.BASIC,
        ))  # block press
        cards: list[type[ds.Card]] = []
        for card in choices:
            for _ in range(choices[card]):
                cards.append(card)

        selection = ds.Cards({})

        def select_card(card: type[ds.Card]) -> None:
            nonlocal selection
            selection = selection.add(card)

        def remove_card(card: type[ds.Card]) -> None:
            nonlocal selection
            selection = selection.remove(card)

        background.add_flet_comp(
            make_centre(
                ft.Row(
                    controls=[
                        self._selectable_card(
                            card,
                            select_card,
                            remove_card,
                        ).root_component
                        for card in cards
                    ],
                    expand=True,
                    wrap=True,
                )
            ),
        )

        def check(_: ft.ControlEvent) -> None:
            last_act_gen = pres[-1]
            try:
                new_act_gen = last_act_gen.choose(selection)
            except Exception:
                dlg = ft.AlertDialog(title=ft.Text("Invalid Selection"))
                dlg.open = True
                self._context.page.dialog = dlg
                self._context.page.update()
                return
            if new_act_gen.filled():
                self.submit_action(new_act_gen.generate_action())
                return
            pres.append(new_act_gen)
            self._act_gen = pres
            self.rerender()
            self.root_component.update()

        def close(_: ft.ControlEvent) -> None:
            assert len(self._act_gen) == 1
            try:
                new_act_gen = self._act_gen[0].choose(ds.ActionType.END_ROUND)
            except Exception:
                dlg = ft.AlertDialog(title=ft.Text("Cannot Cancel"))
                dlg.open = True
                self._context.page.dialog = dlg
                self._context.page.update()
                return
            if new_act_gen.filled():
                self.submit_action(new_act_gen.generate_action())
                return
            self._act_gen.append(new_act_gen)
            self.rerender()
            self.root_component.update()

        background.add_children((
            QItem(
                width_pct=1.0,
                height_pct=0.1,
                anchor=QAnchor(left=0.0, bottom=1.0),
                flets=(
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.icons.CLOSE,
                                on_click=close,
                                style=self._context.settings.button_style,
                            ),
                            ft.IconButton(
                                icon=ft.icons.CHECK,
                                on_click=check,
                                style=self._context.settings.button_style,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        expand=True,
                    ),
                )
            ),
        ))

    def _show_select_chars(self, pres: list[ds.ActionGenerator]) -> None:
        """ Character Selector for Starting Hand Phase """
        choices = pres[-1].choices()
        assert isinstance(choices, tuple) and isinstance(choices[0], int)
        chars = [
            char
            for char in self._curr_state.get_player(self._home_pid).get_characters()
            if char.get_id() in choices
        ]
        self._prompt_action_layer.clear()
        self._prompt_action_layer.add_children((
            background := QItem(
                object_name="click_cover",
                expand=True,
                colour=ft.colors.with_opacity(0.5, "#000000"),
            ),
        ))
        background.add_flet_comp(ft.GestureDetector(
            on_tap=lambda _: None,
            mouse_cursor=ft.MouseCursor.BASIC,
        ))  # block press
        background.add_flet_comp(
            make_centre(
                char_row := ft.Row(
                    expand=True,
                    wrap=True,
                )
            ),
        )

        selection: int | None = None

        char_map: dict[int, QItem] = {}

        def clicked(char_id: int) -> None:
            nonlocal selection
            if selection == char_id:
                return
            for item in char_map.values():
                item.clear()
            selection = char_id
            char_map[char_id].add_children(
                QItem(
                    border=ft.border.all(5, "#00FF00"),
                    expand=True,
                ),
            )
            for item in char_map.values():
                item.root_component.update()

        for char in chars:
            def local_clicked(id: int) -> Callable[[ft.ControlEvent], None]:
                def f(_: ft.ControlEvent) -> None:
                    clicked(id)
                return f
            char_row.controls.append(
                QItem(
                    ref_parent=background,
                    height_pct=0.2,
                    width_height_pct=7 / 12,
                    children=(
                        QText(
                            width_pct=0.9,
                            height_pct=0.9,
                            align=QAlign(x_pct=0.5, y_pct=0.5),
                            colour="#A87845",
                            border=ft.border.all(1, "#DBC9AF"),
                            text=f"{char.name()}",
                            text_colour="#000000",
                            size_rel_height=0.1,
                        ),
                        QImage(
                            expand=True,
                            src=f"assets/char_cards/{char.name()}.png",
                        ),
                        QItem(
                            expand=True,
                            flets=(
                                ft.GestureDetector(
                                    on_tap=local_clicked(char.get_id()),
                                    mouse_cursor=ft.MouseCursor.CLICK,
                                    expand=True,
                                ),
                            ),
                        ),
                        selection_indicator := QItem(
                            expand=True,
                        ),
                    )
                ).root_component
            )
            char_map[char.get_id()] = selection_indicator
        
        def check(_: ft.ControlEvent) -> None:
            last_act_gen = pres[-1]
            try:
                new_act_gen = last_act_gen.choose(selection)
            except Exception:
                dlg = ft.AlertDialog(title=ft.Text("Invalid Selection"))
                dlg.open = True
                self._context.page.dialog = dlg
                self._context.page.update()
                return
            if new_act_gen.filled():
                self.submit_action(new_act_gen.generate_action())
                return
            pres.append(new_act_gen)
            self._act_gen = pres
            self.rerender()
            self.root_component.update()
        
        background.add_children((
            QItem(
                width_pct=1.0,
                height_pct=0.1,
                anchor=QAnchor(left=0.0, bottom=1.0),
                flets=(
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.icons.CHECK,
                                on_click=check,
                                style=self._context.settings.button_style,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        expand=True,
                    ),
                )
            ),
        ))

    def _show_select_dice(self, pres: list[ds.ActionGenerator]) -> None:
        choices = pres[-1].choices()
        assert isinstance(choices, ds.ActualDice)

        self._prompt_action_layer.clear()
        self._prompt_action_layer.add_children((
            background := QItem(
                object_name="click_cover",
                expand=True,
                colour=ft.colors.with_opacity(0.5, "#000000"),
            ),
        ))
        background.add_flet_comp(ft.GestureDetector(
            on_tap=lambda _: None,
            mouse_cursor=ft.MouseCursor.BASIC,
        ))  # block press
        background.add_flet_comp(
            make_centre(
                dice_row := ft.Row(
                    expand=True,
                    wrap=True,
                )
            ),
        )

        is_down: bool = False
        down_id: int = 0

        def on_down(_: ft.ControlEvent) -> None:
            nonlocal is_down
            nonlocal down_id
            down_id += 1
            is_down = True

        def on_release(_: ft.ControlEvent) -> None:
            nonlocal is_down
            is_down = False

        background.add_flet_comp(
            ft.TransparentPointer(
                content=ft.GestureDetector(
                    on_pan_start=on_down,
                    on_pan_end=on_release,
                ),
                expand=True,
            )
        )

        selection: dict[ds.Element, int] = defaultdict(int)

        selection_timestamp: dict[tuple[ds.Element, int], int] = defaultdict(int)
        selection_status: dict[tuple[ds.Element, int], bool] = defaultdict(bool)
        selection_frames: dict[tuple[ds.Element, int], QItem] = {}

        def select_elem(elem: ds.Element) -> None:
            selection[elem] += 1

        def remove_elem(elem: ds.Element) -> None:
            selection[elem] -= 1

        def flip_die(elem: ds.Element, id: int) -> None:
            if selection_status[(elem, id)]:
                remove_elem(elem)
                selection_frames[(elem, id)].clear()
            else:
                select_elem(elem)
                selection_frames[(elem, id)].add_children((
                    QItem(
                        expand=True,
                        border=ft.border.all(5, "#00FF00"),
                    ),
                ))
            selection_frames[(elem, id)].root_component.update()
            selection_status[(elem, id)] = not selection_status[(elem, id)]

        def enter_die(elem: ds.Element, id: int) -> Callable[[ft.ControlEvent], None]:
            def f(_: ft.ControlEvent) -> None:
                if not is_down:
                    return
                if selection_timestamp[(elem, id)] == down_id:
                    return
                selection_timestamp[(elem, id)] = down_id
                flip_die(elem, id)
            return f

        def tap_die(elem: ds.Element, id: int) -> Callable[[ft.ControlEvent], None]:
            def f(_: ft.ControlEvent) -> None:
                flip_die(elem, id)
            return f

        for elem in choices.readonly_dice_ordered(self._curr_state.get_player(self._home_pid)):
            for i in range(choices[elem]):
                dice_row.controls.append(
                    QItem(
                        ref_parent=background,
                        height_pct=0.07,
                        width_height_pct=1.0,
                        children=(
                            self._die(elem),
                            frame := QItem(
                                expand=True,
                            )
                        ),
                        flets=(
                            ft.GestureDetector(
                                on_tap=tap_die(elem, i),
                                on_enter=enter_die(elem, i),
                                mouse_cursor=ft.MouseCursor.CLICK,
                                expand=True,
                            ),
                        ),
                    ).root_component
                )
                selection_frames[(elem, i)] = frame

        def close(_: ft.ControlEvent) -> None:
            self.submit_action(ds.EndRoundAction())

        def check(_: ft.ControlEvent) -> None:
            last_act_gen = pres[-1]
            try:
                new_act_gen = last_act_gen.choose(ds.ActualDice(selection))
            except Exception:
                dlg = ft.AlertDialog(title=ft.Text("Invalid Selection"))
                dlg.open = True
                self._context.page.dialog = dlg
                self._context.page.update()
                return
            if new_act_gen.filled():
                self.submit_action(new_act_gen.generate_action())
                return
            pres.append(new_act_gen)
            self._act_gen = pres
            self.rerender()
            self.root_component.update()
        
        background.add_children((
            QItem(
                width_pct=1.0,
                height_pct=0.1,
                anchor=QAnchor(left=0.0, bottom=1.0),
                flets=(
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.icons.CLOSE,
                                on_click=close,
                                style=self._context.settings.button_style,
                            ),
                            ft.IconButton(
                                icon=ft.icons.CHECK,
                                on_click=check,
                                style=self._context.settings.button_style,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        expand=True,
                    ),
                )
            ),
        ))

    def _selectable_card(
            self,
            card: type[ds.Card],
            on_selected: Callable[[type[ds.Card]], None] = lambda _: None,
            on_removed: Callable[[type[ds.Card]], None] = lambda _: None,
    ) -> QItem:
        selected = False
        item = QItem(
            ref_parent=self._prompt_action_layer,
            height_pct=0.15,
            width_height_pct=7 / 12,
            children=(
                QText(
                    width_pct=0.9,
                    height_pct=0.9,
                    align=QAlign(x_pct=0.5, y_pct=0.5),
                    colour="#A87845",
                    border=ft.border.all(1, "#DBC9AF"),
                    text=f"{card.__name__}",
                    text_colour="#000000",
                    size_rel_height=0.1,
                ),
                QImage(
                    expand=True,
                    src=f"assets/cards/{card.name()}Card.png",
                ),
                click_pane := QItem(
                    expand=True,
                ),
                selection_indicator := QItem(
                    expand=True,
                )
            ),
        )

        def clicked(_: ft.ControlEvent) -> None:
            nonlocal selected
            if selected:
                selected = False
                on_removed(card)
                selection_indicator.clear()
            else:
                selected = True
                on_selected(card)
                selection_indicator.add_children((
                    QItem(
                        border=ft.border.all(5, "#00FF00"),
                        expand=True,
                    ),
                ))
            selection_indicator.root_component.update()

        click_pane.add_flet_comp(ft.GestureDetector(
            on_tap=clicked,
            mouse_cursor=ft.MouseCursor.CLICK,
            expand=True,
        ))
        return item

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
                QText(
                    expand=True,
                    text=f"{support.__class__.__name__}",
                    text_colour="#000000",
                    size_rel_height=0.1,
                ),
                QImage(
                    object_name="support-img",
                    src=f"assets/supports/{support.__class__.__name__}.png",
                    border=ft.border.all(1, "#DBC9AF"),
                    expand=True,
                ),
            ),
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
                    children=(
                        QText(
                            height_pct=1.0,
                            width_pct=2.0,
                            align=QAlign(x_pct=0.5, y_pct=0.5),
                            text=f"{support.usages}",
                            text_colour="#FFFFFF",
                            size_rel_height=0.6,
                        ),
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
                QText(
                    expand=True,
                    text=f"{summon.__class__.__name__}",
                    text_colour="#000000",
                    size_rel_height=0.1,
                ),
                QImage(
                    object_name="summon-img",
                    src=f"assets/summons/{summon.__class__.__name__}.png",
                    border=ft.border.all(1, "#DBC9AF"),
                    expand=True,
                ),
                QItem(
                    object_name="summon-count-down",
                    height_pct=0.2,
                    width_height_pct=1.0,
                    align=QAlign(x_pct=0.95, y_pct=0.05),
                    colour="#887054",
                    border=ft.border.all(1, "#DBC9AF"),
                    children=(
                        QText(
                            height_pct=1.0,
                            width_pct=2.0,
                            align=QAlign(x_pct=0.5, y_pct=0.5),
                            text=f"{summon.usages}",
                            text_colour="#FFFFFF",
                            size_rel_height=0.6,
                        ),
                    ),
                ),
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
        is_active = char.get_id() == chars.get_active_character_id()
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
                            colour="#A87845",
                            border=ft.border.all(1, "#DBC9AF"),
                            children=(
                                QText(
                                    expand=True,
                                    text=f"{char.name()}",
                                    text_colour="#000000",
                                    size_rel_height=0.15,
                                ),
                                QImage(
                                    expand=True,
                                    src=f"assets/char_cards/{char.name()}75.png",
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        )
        if char.defeated():
            char_card.add_children((
                QItem(
                    expand=True,
                    colour=ft.colors.with_opacity(0.7, "#000000"),
                ),
            ))
            return item
        if char.get_hp() == 0:
            char_card.add_children((
                QItem(
                    expand=True,
                    colour=ft.colors.with_opacity(0.5, "#000000"),
                ),
            ))

        def show_char_detail(_: ft.ControlEvent) -> None:
            def exit(_: ft.ControlEvent) -> None:
                self._info_layer.clear()
                self._context.page.update()

            self._info_layer.add_flet_comp((
                ft.Container(
                    content=ft.GestureDetector(
                        on_tap=exit,
                        mouse_cursor=ft.MouseCursor.CLICK,
                    ),
                    expand=True,
                    bgcolor=ft.colors.with_opacity(0.7, "#000000"),
                ),
            ))
            hidden_statuses = char.get_hidden_statuses()
            equipment_statues = char.get_equipment_statuses()
            character_statuses = char.get_character_statuses()
            content = '\n'.join((
                "<Implicit Statuses>",
                '\n'.join([
                    "    - " + s
                    for s in hidden_statuses.dict_str()
                ]),
                "\n<Equipment Statuses>",
                '\n'.join([
                    "    - " + s
                    for s in equipment_statues.dict_str()
                ]),
                "\n<Character Statuses>",
                '\n'.join([
                    "    - " + s
                    for s in character_statuses.dict_str()
                ]),
            ))
            optional_content = ""
            if is_active:
                combat_status = game_state.get_player(pid).get_combat_statuses()
                optional_content = '\n'.join((
                    "\n\n<Combat Statuses>",
                    '\n'.join([
                        "    - " + s
                        for s in combat_status.dict_str()
                    ]),
                ))
            self._info_layer.add_children((
                QText(
                    expand=True,
                    text=content + optional_content,
                    text_colour="#FFFFFF",
                    text_alignment=ft.alignment.top_left,
                    size_rel_height=0.02,
                ),
            ))
            self._context.page.update()

        char_card.add_flet_comp((
            ft.GestureDetector(
                on_tap=show_char_detail,
                mouse_cursor=ft.MouseCursor.CLICK,
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
                rotate=ft.Rotate(angle=0.25 * pi, alignment=ft.alignment.center),
            ),
            equip_item := QItem(
                object_name=f"char-{pid}-{char_id}-{char.name()}-equip",
                height_pct=0.8,
                width_pct=0.22,
                anchor=QAnchor(left=-0.11, top=0.2),
            ),
        ))
        hp_item.add_children(
            QText(
                text=f"{char.get_hp()}",
                text_colour="#FFFFFF",
                size_rel_height=0.6,
                rotate=ft.Rotate(angle=-0.25 * pi, alignment=ft.alignment.center),
                width_pct=2.0,
                height_pct=1.0,
                align=QAlign(x_pct=0.5, y_pct=0.5),
            )
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
                border_radius=0x7fffffff,
                border=ft.border.all(1, "#DBC9AF"),
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
                    rotate=ft.Rotate(angle=0.25 * pi, alignment=ft.alignment.center),
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
        char_card.add_children((
            char_status_row_item := QItem(
                width_pct=1.0,
                height_pct=0.15,
                anchor=QAnchor(left=0.0, bottom=0.99),
            ),
        ))
        for i, status in enumerate(char.get_character_statuses()):
            if i > 3:
                break
            char_status_row_item.add_children((
                QImage(
                    height_pct=1.0,
                    width_height_pct=1.0,
                    anchor=QAnchor(left=i * 0.25, top=0.0),
                    src=f"assets/icons/StatusIcon.png",
                ),
            ))
        if is_active:
            char_card.add_children((
                combat_status_row_item := QItem(
                    width_pct=1.0,
                    height_pct=0.15,
                    anchor=QAnchor(left=0.0, top=1.01),
                ),
            ))
            for i, status in enumerate(game_state.get_player(pid).get_combat_statuses()):
                if i > 3:
                    break
                combat_status_row_item.add_children((
                    QImage(
                        height_pct=1.0,
                        width_height_pct=1.0,
                        anchor=QAnchor(left=i * 0.25, top=0.0),
                        src=f"assets/icons/StatusIcon.png",
                    ),
                ))
        return item

    ELEM_NAME_MAP: ds.HashableDict[ds.Element, str] = ds.HashableDict({
        ds.Element.PYRO: "Pyro",
        ds.Element.HYDRO: "Hydro",
        ds.Element.ANEMO: "Anemo",
        ds.Element.ELECTRO: "Electro",
        ds.Element.DENDRO: "Dendro",
        ds.Element.CRYO: "Cryo",
        ds.Element.GEO: "Geo",
        ds.Element.OMNI: "Omni",
        ds.Element.ANY: "Any",
    })

    def _dice(
            self,
            pid: ds.Pid,
            game_state: ds.GameState,
    ) -> QItem:
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
                    info_row_item := QItem(
                        height_pct=1.0 / 22 * 9,
                        width_pct=1.0,
                        anchor=QAnchor(left=0.0, bottom=1.0),
                        flets=(
                            info_row := ft.Row(
                                expand=True,
                            ),
                        ),
                    ),
                ),
            )
            card_info = QItem(
                ref_parent=item,
                height_pct=1.0 / 22 * 9,
                width_height_pct=7 / 12,
                colour="#000000",
                children=(
                    QImage(
                        src=f"assets/cards/OmniCardCard.png",
                        expand=True,
                    ),
                    QText(
                        expand=True,
                        colour=ft.colors.with_opacity(0.2, "#000000"),
                        text=f"{game_state.get_player(pid).get_deck_cards().num_cards()}",
                        text_colour="#FFFFFF",
                        size_rel_height=0.2,
                    ),
                ),
            )
            dice_info = QItem(
                ref_parent=item,
                height_pct=0.5 / 22 * 9,
                width_height_pct=1.0,
                children=(
                    QImage(
                        src=f"assets/dice/{self.ELEM_NAME_MAP[ds.Element.ANY]}Die.png",
                        expand=True,
                    ),
                    QText(
                        expand=True,
                        text=f"{dice.num_dice()}",
                        text_colour="#FFFFFF",
                        size_rel_height=0.4,
                    ),
                )
            )
            info_row.controls.extend((card_info.root_component, dice_info.root_component))
            if game_state.get_player(self._home_pid).in_action_phase():
                info_row.controls.append(
                    QImage(
                        ref_parent=card_info,
                        height_pct=0.7,
                        width_height_pct=1.0,
                        src=f"assets/gif/active.gif",
                    ).root_component
                )
            dice_row_item.add_flet_comp((
                ft.Row(
                    controls=[
                        QItem(
                            ref_parent=dice_row_item,
                            height_pct=1.0,
                            width_height_pct=1.0,
                            children=(
                                self._die(elem),
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
                        src=f"assets/dice/{self.ELEM_NAME_MAP[ds.Element.ANY]}Die.png",
                        expand=True,
                    ),
                    QText(
                        expand=True,
                        text=f"{dice.num_dice()}",
                        text_colour="#FFFFFF",
                        size_rel_height=0.4,
                    ),
                ),
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
                    QText(
                        expand=True,
                        colour=ft.colors.with_opacity(0.2, "#000000"),
                        text=f"{game_state.get_player(pid).get_deck_cards().num_cards()}",
                        text_colour="#FFFFFF",
                        size_rel_height=0.2,
                    ),
                ),
            )
            info_row.controls.extend((
                card_info.root_component,
                dice_info.root_component,
            ))
            if game_state.get_player(self._home_pid.other()).in_action_phase():
                info_row.controls.append(
                    QImage(
                        ref_parent=card_info,
                        height_pct=0.7,
                        width_height_pct=1.0,
                        src=f"assets/gif/active.gif",
                    ).root_component
                )
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
                QText(
                    width_pct=0.9,
                    height_pct=0.9,
                    align=QAlign(x_pct=0.5, y_pct=0.5),
                    colour="#A87845",
                    border=ft.border.all(1, "black"),
                    text=card.name(),
                    text_colour="#FFFFFF",
                    size_rel_height=0.1,
                ),
                QImage(
                    src=f"assets/cards/{card.name()}Card.png",
                    expand=True,
                ),
            ),
        )
        return item

    def _die(self, elem: ds.Element) -> QItem:
        return QItem(
            expand=True,
            children=(
                QImage(
                    src=f"assets/dice/{self.ELEM_NAME_MAP[elem]}Die.png",
                    expand=True,
                ),
                QImage(
                    src=f"assets/elem_icons/{self.ELEM_NAME_MAP[elem]}.png",
                    width_pct=0.7,
                    height_pct=0.7,
                    align=QAlign(x_pct=0.5, y_pct=0.5),
                ),
            ),
        )
