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
from __future__ import annotations
from collections import defaultdict, Counter
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
    def pre_removal(self) -> None:
        self._listener.unsubscribe()

    def _swap_view(self, _: ft.ControlEvent) -> None:
        self._home_pid = self._home_pid.other()
        self._prompt_action_layer.clear()
        self.rerender()
        self.root_component.update()

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
        self._button_settings = ft.IconButton(
            icon=ft.icons.SETTINGS,
            on_click=self._show_settings,
            style=context.settings.button_style,
        )
        self._button_history = ft.IconButton(
            icon=ft.icons.ACCESS_TIME,
            on_click=self._show_history,
            style=context.settings.button_style,
        )
        self._button_swap_view = ft.IconButton(
            icon=ft.icons.WIFI_PROTECTED_SETUP,
            on_click=self._swap_view,
            style=self._context.settings.button_style,
        )

        self._home_pid = ds.Pid.P1
        self._base_act_gen: ds.ActionGenerator | None = None
        self._act_gen: list[ds.ActionGenerator] = []
        self._listener = self._context.game_data.new_listener()
        self._in_history = False

        def on_update() -> None:
            self.rerender()
            self.root_component.update()
        self._listener.on_update = on_update
        self.rerender()

    def _back_to_home(self, _: Any) -> None:
        self._context.current_route = Route.GAME

    def _on_act_gen_updated(self) -> None:
        if len(self._act_gen) == 0:
            return
        if self._act_gen[-1].filled():
            self.submit_action(self._act_gen[-1].generate_action())
        else:
            self.render_prompt_action()
            self._prompt_action_layer.root_component.update()

    def submit_action(self, action: ds.PlayerAction) -> None:
        self._base_act_gen = None
        self._act_gen.clear()
        self._context.game_data.take_action(self._home_pid, action)

    def rerender(self, _: Any = None) -> None:
        self._curr_state = self._context.game_data.curr_game_state(self._home_pid)
        self._base_act_gen = None
        self._act_gen.clear()
        game_mode = self._context.game_data.curr_game_mode
        if (
                self._curr_state.waiting_for() is self._home_pid
                and (
                    self._home_pid is game_mode.primary_player
                    or (
                        game_mode.local
                        and game_mode.setting_of(self._home_pid).player_type == "P"
                    )
                )
                and not self._curr_state.game_end()
        ):
            self._base_act_gen = self._curr_state.action_generator(self._home_pid)
            self._act_gen.append(self._base_act_gen)
        self.render_prompt_action()
        self.render_state(self._curr_state)
        if self._curr_state.game_end():
            winner = self._curr_state.get_winner()
            if winner is None:
                text = "Draw"
            elif winner is self._home_pid:
                text = "Win"
            elif winner is self._home_pid.other():
                text = "Lose"
            else:
                raise Exception("Invalid winner")
            self._game_layer.add_children((
                QText(
                    width_pct=0.7,
                    height_pct=0.1,
                    align=QAlign(x_pct=0.5, y_pct=0.5),
                    colour=ft.colors.with_opacity(0.5, "#000000"),
                    text=text,
                    text_colour="#FFFFFF",
                    size_rel_height=0.4,
                )
            ))

        if self._in_history:
            self._show_history(None)

    def render_state(self, game_state: ds.GameState) -> None:
        self._top_right_col_menu.controls.clear()
        self._top_right_col_menu.controls.append(self._button_exit)
        self._top_right_col_menu.controls.append(self._button_settings)
        self._top_right_col_menu.controls.append(self._button_history)
        game_mode = self._context.game_data.curr_game_mode
        assert game_mode is not None
        if (
                game_mode.local
                and game_mode.primary_settings.player_type == "P"
                and game_mode.oppo_settings.player_type == "P"
        ):
            self._top_right_col_menu.controls.append(self._button_swap_view)
        self._game_layer.clear()

        self._game_layer.add_children((
            self._card_zone(0.005, 0.09, self._home_pid.other(), game_state),
            self._support_summon_zone(0.105, 0.09, self._home_pid.other(), game_state),
            self._char_zone(0.205, 0.22, self._home_pid.other(), game_state),
            self._char_zone(0.435, 0.22, self._home_pid, game_state),
            self._support_summon_zone(0.665, 0.09, self._home_pid, game_state),
            self._card_zone(0.765, 0.22, self._home_pid, game_state),
            self._end_round(self._home_pid, game_state),
        ))

    def render_prompt_action(self) -> None:
        self._prompt_action_layer.clear()
        if self._base_act_gen is None or self._in_history:
            return
        if len(self._act_gen) == 1:
            mode = self._curr_state.mode
            choices = self._base_act_gen.choices()
            if self._curr_state.death_swapping(self._home_pid):
                self._show_select_chars([
                    self._base_act_gen,
                    self._base_act_gen.choose(ds.ActionType.SWAP_CHARACTER),
                ])
                return
            match type(self._curr_state.phase):
                case mode.card_select_phase:
                    if ds.ActionType.SELECT_CARDS in choices:
                        self._show_select_cards([
                            self._base_act_gen,
                            self._base_act_gen.choose(ds.ActionType.SELECT_CARDS),
                        ])
                case mode.starting_hand_select_phase:
                    self._show_select_chars([self._base_act_gen])
                case mode.roll_phase:
                    if ds.ActionType.SELECT_DICE in choices:
                        self._show_select_dice([
                            self._base_act_gen,
                            self._base_act_gen.choose(ds.ActionType.SELECT_DICE),
                        ])
                    else:
                        self.submit_action(ds.EndRoundAction())
                case mode.action_phase:
                    if ds.ActionType.SELECT_DICE in choices:
                        self._show_select_dice([
                            self._base_act_gen,
                            self._base_act_gen.choose(ds.ActionType.SELECT_DICE),
                        ])
                    elif ds.ActionType.SELECT_CARDS in choices:
                        self._show_select_cards([
                            self._base_act_gen,
                            self._base_act_gen.choose(ds.ActionType.SELECT_CARDS),
                        ])
        else:
            assert len(self._act_gen) > 1
            choices = self._act_gen[-1].choices()
            latest_action = self._act_gen[-1].action
            if isinstance(choices, ds.AbstractDice):
                self._show_select_dice(list(self._act_gen))
            elif isinstance(choices, tuple):
                if isinstance(latest_action, ds.SwapAction) and latest_action.char_id is None:
                    self._show_select_chars(list(self._act_gen))
                elif isinstance(latest_action, ds.ElementalTuningAction):
                    if latest_action.card is None:
                        self._show_select_card()
                    elif latest_action.dice_elem is None:
                        self._show_select_die(list(self._act_gen))
                elif isinstance(choices[0], ds.StaticTarget):
                    self._show_select_static_target(list(self._act_gen))
                elif issubclass(choices[0], ds.Card):
                    self._show_select_card()
                else:
                    print("choices:", choices)
                    print("len actions:", len(self._act_gen))
                    print("action type:", type(self._act_gen[-1].action))
            else:
                print("choices:", choices)

    def _prompt_layer_bg(self) -> tuple[QItem, QItem]:
        reveal = QItem(
            expand=True,
        )
        background = QItem(
            object_name="click_cover",
            expand=True,
            colour=ft.colors.with_opacity(0.5, "#000000"),
        )

        def show_content(_: ft.ControlEvent) -> None:
            background.root_component.visible = True
            background.root_component.update()

        def hide_content(_: ft.ControlEvent) -> None:
            background.root_component.visible = False
            background.root_component.update()

        reveal.add_flet_comp(ft.GestureDetector(
            on_tap=show_content,
            mouse_cursor=ft.MouseCursor.CLICK,
        ))
        background.add_flet_comp((
            ft.GestureDetector(  # block press
                on_tap=lambda _: None,
                mouse_cursor=ft.MouseCursor.BASIC,
            ),
            ft.Container(
                content=ft.IconButton(
                    icon=ft.icons.REMOVE_RED_EYE_OUTLINED,
                    style=self._context.settings.button_style,
                    on_click=hide_content,
                ),
                alignment=ft.alignment.top_right,
            ),
        ))
        return reveal, background

    def _show_settings(self, _: ft.ControlEvent) -> None:
        self._prompt_action_layer.clear()
        reveal, background = self._prompt_layer_bg()
        self._prompt_action_layer.add_children((reveal, background))

        background.add_flet_comp(
            make_centre(
                buttons_col := ft.Column(
                    expand=True,
                    wrap=True,
                )
            )
        )

        def close(_: ft.ControlEvent) -> None:
            self._prompt_action_layer.clear()
            self._prompt_action_layer.root_component.update()

        background.add_children((
            QItem(
                width_pct=1.0,
                height_pct=0.1,
                anchor=QAnchor(left=0.0, bottom=1.0),
                flets=(
                    control_row := ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        expand=True,
                    ),
                )
            ),
        ))

        control_row.controls.append(
            ft.IconButton(
                icon=ft.icons.CLOSE,
                on_click=close,
                style=self._context.settings.button_style,
            ),
        )
        
        assert self._context.game_data.curr_game_mode is not None
        if self._context.game_data.curr_game_mode.local:
            buttons_col.controls.append(
                ft.TextButton(
                    text="Swap View",
                    icon=ft.icons.WIFI_PROTECTED_SETUP,
                    on_click=self._swap_view,
                    style=self._context.settings.button_style,
                )
            )

        if (
                self._home_pid is self._context.game_data.curr_game_mode.primary_player
                or (
                    self._context.game_data.curr_game_mode.local
                    and self._context.game_data.curr_game_mode.setting_of(self._home_pid).player_type == "P"
                )
        ):
            def surrender(_: ft.ControlEvent) -> None:
                self._context.game_data.surrender(self._home_pid)
                self.rerender()
                self.root_component.update()

            buttons_col.controls.append(
                ft.TextButton(
                    text="Surrender",
                    icon=ft.icons.FLAG,
                    on_click=surrender,
                    style=self._context.settings.button_style,
                )
            )

        self._prompt_action_layer.root_component.update()

    def _show_history(self, _: ft.ControlEvent) -> None:
        self._in_history = True
        self._prompt_action_layer.clear()
        reveal, background = self._prompt_layer_bg()
        self._prompt_action_layer.add_children((reveal, background))

        def close(_: ft.ControlEvent) -> None:
            self._prompt_action_layer.clear()
            self._prompt_action_layer.root_component.update()
            if self._context.game_data.is_at_latest():
                print("======== is at latest")
                self._in_history = False
                self.rerender()
                self.root_component.update()

        background.add_flet_comp(
            ft.GestureDetector(
                on_tap=close,
                mouse_cursor=ft.MouseCursor.BASIC,
                expand=True,
            )
        )

        state_index = self._context.game_data.curr_state_index()
        contents = [
            f"State: {state_index[0]} | {state_index[1]}",
            f"Round: {self._curr_state.round}",
            f"Phase: {self._curr_state.phase.__class__.__name__}",
        ]
        action_taken = self._context.game_data.action_taken_at_curr(self._home_pid)
        if action_taken is not None:
            contents.append(f"Action from: {self._curr_state.waiting_for().name}")
            contents.append(f"Action: {action_taken}")
        text_content = '\n'.join(contents)

        background.add_children(
            QText(
                width_pct=0.8,
                height_pct=0.8,
                align=QAlign(x_pct=0.5, y_pct=0.5),
                text=text_content,
                text_colour="#FFFFFF",
                size_rel_height=0.03,
            )
        )

        background.add_children((
            QItem(
                width_pct=1.0,
                height_pct=0.1,
                anchor=QAnchor(left=0.0, bottom=1.0),
                flets=(
                    control_row := ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        expand=True,
                    ),
                )
            ),
        ))

        def action_back(_: ft.ControlEvent) -> None:
            self._context.game_data.action_back()
            self.rerender()
            self.root_component.update()

        def action_forward(_: ft.ControlEvent) -> None:
            self._context.game_data.action_forward()
            self.rerender()
            self.root_component.update()

        def step_back(_: ft.ControlEvent) -> None:
            self._context.game_data.step_back()
            self.rerender()
            self.root_component.update()

        def step_forward(_: ft.ControlEvent) -> None:
            self._context.game_data.step_forward()
            self.rerender()
            self.root_component.update()

        control_row.controls.append(
            ft.IconButton(
                icon=ft.icons.KEYBOARD_DOUBLE_ARROW_LEFT,
                on_click=action_back,
                style=self._context.settings.button_style,
            )
        )
        control_row.controls.append(
            ft.IconButton(
                icon=ft.icons.KEYBOARD_ARROW_LEFT,
                on_click=step_back,
                style=self._context.settings.button_style,
            )
        )
        control_row.controls.append(
            ft.IconButton(
                icon=ft.icons.KEYBOARD_ARROW_RIGHT,
                on_click=step_forward,
                style=self._context.settings.button_style,
            )
        )
        control_row.controls.append(
            ft.IconButton(
                icon=ft.icons.KEYBOARD_DOUBLE_ARROW_RIGHT,
                on_click=action_forward,
                style=self._context.settings.button_style,
            )
        )

        self.root_component.update()

    def _show_select_cards(self, pres: list[ds.ActionGenerator]) -> None:
        self._prompt_action_layer.clear()
        reveal, background = self._prompt_layer_bg()
        self._prompt_action_layer.add_children((reveal, background))

        choices = pres[-1].choices()
        assert isinstance(choices, ds.Cards)
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
            pres.append(new_act_gen)
            self._act_gen = pres
            self._on_act_gen_updated()

        def close(_: ft.ControlEvent) -> None:
            assert len(self._act_gen) > 1
            self._act_gen = self._act_gen[:-1]
            self._on_act_gen_updated()

        background.add_children((
            QItem(
                width_pct=1.0,
                height_pct=0.1,
                anchor=QAnchor(left=0.0, bottom=1.0),
                flets=(
                    control_row := ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        expand=True,
                    ),
                )
            ),
        ))
        if len(self._act_gen) > 1:
            control_row.controls.append(
                ft.IconButton(
                    icon=ft.icons.CLOSE,
                    on_click=close,
                    style=self._context.settings.button_style,
                ),
            )
        control_row.controls.append(
            ft.IconButton(
                icon=ft.icons.CHECK,
                on_click=check,
                style=self._context.settings.button_style,
            ),
        )

    def _show_select_card(self) -> None:
        """ Only used for previewing hand cards and possibly action """
        self._prompt_action_layer.clear()
        reveal, background = self._prompt_layer_bg()
        self._prompt_action_layer.add_children((reveal, background))

        cards = self._curr_state.get_player(self._home_pid).hand_cards
        cards = list(Counter(cards.to_dict()).elements())

        last_selection: QItem | None = None
        selected_card: type[ds.Card] | None = None

        control_row: ft.Row

        def close(_: ft.ControlEvent) -> None:
            if len(self._act_gen) > 1:
                self._act_gen = self._act_gen[:1]
            self._prompt_action_layer.clear()
            self._prompt_action_layer.root_component.update()

        def tune(_: ft.ControlEvent) -> None:
            self._act_gen = [
                self._base_act_gen,
                cards_act_gen := self._base_act_gen.choose(ds.ActionType.ELEMENTAL_TUNING),
                cards_act_gen.choose(selected_card),
            ]
            self._on_act_gen_updated()

        def play(_: ft.ControlEvent) -> None:
            self._act_gen = [
                self._base_act_gen,
                cards_act_gen := self._base_act_gen.choose(ds.ActionType.PLAY_CARD),
                cards_act_gen.choose(selected_card),
            ]
            self._on_act_gen_updated()

        close_button = ft.IconButton(
            icon=ft.icons.CLOSE,
            on_click=close,
            style=self._context.settings.button_style,
        )

        tune_button = ft.IconButton(
            icon=ft.icons.RESTORE_FROM_TRASH,
            style=self._context.settings.button_style,
            icon_color="#000000",
        )

        play_button = ft.IconButton(
            icon=ft.icons.CHECK,
            style=self._context.settings.button_style,
            icon_color="#000000",
        )

        def click_card(card: type[ds.Card], selection_indicator: QItem) -> Callable:
            def f(_: ft.ControlEvent) -> None:
                nonlocal last_selection
                nonlocal selected_card

                selected_card = card
                duplicate_click = last_selection is selection_indicator
                if last_selection is not None:
                    last_selection.clear()
                last_selection = selection_indicator
                last_selection.add_children((
                    QItem(
                        expand=True,
                        border=ft.border.all(5, "#00FF00"),
                    ),
                ))
                control_row.clean()
                control_row.controls.append(close_button)
                control_row.controls.append(tune_button)
                control_row.controls.append(play_button)
                if self._base_act_gen is None:
                    background.root_component.update()
                    return
                if (
                        ds.ActionType.ELEMENTAL_TUNING in self._base_act_gen.choices()
                        and card in self._base_act_gen.choose(ds.ActionType.ELEMENTAL_TUNING).choices()
                ):
                    tune_button.icon_color = "#FFFFFF"
                    tune_button.on_click = tune
                else:
                    tune_button.icon_color = "#000000"
                    tune_button.on_click = lambda _: None
                if (
                        ds.ActionType.PLAY_CARD in self._base_act_gen.choices()
                        and card in self._base_act_gen.choose(ds.ActionType.PLAY_CARD).choices()
                ):
                    play_button.icon_color = "#FFFFFF"
                    play_button.on_click = play
                    if duplicate_click:
                        play(None)  # type: ignore
                        return
                else:
                    play_button.icon_color = "#000000"
                    play_button.on_click = lambda _: None
                background.root_component.update()
            return f

        background.add_flet_comp(
            make_centre(
                ft.Row(
                    controls=[
                        QItem(
                            ref_parent=background,
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
                                selection_indicator := QItem(
                                    expand=True,
                                ),
                                click_pane := QItem(
                                    expand=True,
                                    flets=(
                                        ft.GestureDetector(
                                            on_tap=click_card(card, selection_indicator),
                                            mouse_cursor=ft.MouseCursor.CLICK,
                                            expand=True,
                                            visible=not self._in_history,
                                        ),
                                    ),
                                ),
                            ),
                        ).root_component
                        for card in cards
                    ],
                    expand=True,
                    wrap=True,
                )
            ),
        )

        background.add_children((
            QItem(
                width_pct=1.0,
                height_pct=0.1,
                anchor=QAnchor(left=0.0, bottom=1.0),
                flets=(
                    control_row := ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        expand=True,
                    ),
                )
            ),
        ))

        control_row.controls.append(close_button)

    def _show_select_chars(self, pres: list[ds.ActionGenerator]) -> None:
        """ Character Selector for Starting Hand Phase """
        self._prompt_action_layer.clear()
        reveal, background = self._prompt_layer_bg()
        self._prompt_action_layer.add_children((reveal, background))

        choices = pres[-1].choices()
        assert isinstance(choices, tuple) and isinstance(choices[0], int)
        chars = [
            char
            for char in self._curr_state.get_player(self._home_pid).characters
            if char.id in choices
        ]

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

        click_button = ft.IconButton(
            icon=ft.icons.CHECK,
            style=self._context.settings.button_style,
            icon_color="#000000",
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
            pres.append(new_act_gen)
            self._act_gen = pres
            self._on_act_gen_updated()

        def close(_: ft.ControlEvent) -> None:
            assert len(self._act_gen) > 1
            self._act_gen = self._act_gen[:-1]
            self._on_act_gen_updated()

        def clicked(char_id: int) -> None:
            nonlocal selection
            if selection == char_id:
                check(None)  # type: ignore
                return
            for item in char_map.values():
                item.clear()
            selection = char_id
            if click_button.icon_color == "#000000":
                click_button.icon_color = "#FFFFFF"
                click_button.on_click = check
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
                            src=f"assets/char-cards/{char.name()}.png",
                        ),
                        QItem(
                            expand=True,
                            flets=(
                                ft.GestureDetector(
                                    on_tap=local_clicked(char.id),
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
            char_map[char.id] = selection_indicator

        background.add_children((
            QItem(
                width_pct=1.0,
                height_pct=0.1,
                anchor=QAnchor(left=0.0, bottom=1.0),
                flets=(
                    control_row := ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        expand=True,
                    ),
                )
            ),
        ))
        if len(self._act_gen) > 1:
            control_row.controls.append(
                ft.IconButton(
                    icon=ft.icons.CLOSE,
                    on_click=close,
                    style=self._context.settings.button_style,
                ),
            )
        control_row.controls.append(
            click_button
        )

    def _show_select_die(self, pres: list[ds.ActionGenerator]) -> None:
        self._prompt_action_layer.clear()
        reveal, background = self._prompt_layer_bg()
        self._prompt_action_layer.add_children((reveal, background))
        background.add_flet_comp((
            make_centre(
                dice_row := ft.Row(
                    expand=True,
                    wrap=True,
                )
            ),
        ))

        last_selection_indicator: QItem | None = None
        selected_die: ds.Element | None = None

        def close(_: ft.ControlEvent) -> None:
            assert len(self._act_gen) > 1
            self._act_gen = self._act_gen[:-1]
            self._on_act_gen_updated()
        
        def check(_: ft.ControlEvent) -> None:
            last_act_gen = pres[-1]
            try:
                new_act_gen = last_act_gen.choose(selected_die)
            except Exception:
                dlg = ft.AlertDialog(title=ft.Text("Invalid Selection"))
                dlg.open = True
                self._context.page.dialog = dlg
                self._context.page.update()
                return
            pres.append(new_act_gen)
            self._act_gen = pres
            self._on_act_gen_updated()

        close_button = ft.IconButton(
            icon=ft.icons.CLOSE,
            on_click=close,
            style=self._context.settings.button_style,
        )

        check_button = ft.IconButton(
            icon=ft.icons.CHECK,
            style=self._context.settings.button_style,
            icon_color="#000000",
        )

        choices: tuple[ds.Element] = pres[-1].choices()
        assert isinstance(choices, tuple), choices
        assert isinstance(choices[0], ds.Element), choices

        def elem_clicked(elem: ds.Element, selection_indicator: QItem) -> Callable:
            def f(_: ft.ControlEvent) -> None:
                nonlocal last_selection_indicator
                nonlocal selected_die

                selected_die = elem
                if last_selection_indicator is selection_indicator:
                    check(None)  # type: ignore
                    return
                if last_selection_indicator is not None:
                    last_selection_indicator.clear()
                last_selection_indicator = selection_indicator
                last_selection_indicator.add_children((
                    QItem(
                        expand=True,
                        border=ft.border.all(5, "#00FF00"),
                    ),
                ))
                if check_button.icon_color == "#000000":
                    check_button.icon_color = "#FFFFFF"
                    check_button.on_click = check
                background.root_component.update()
            return f

        for elem in choices:
            dice_row.controls.append(
                QItem(
                    ref_parent=background,
                    height_pct=0.07,
                    width_height_pct=1.0,
                    children=(
                        self._die(elem),
                        selection_indicator := QItem(
                            expand=True,
                        ),
                        click_pane := QItem(
                            expand=True,
                            flets=(
                                ft.GestureDetector(
                                    on_tap=elem_clicked(elem, selection_indicator),
                                    mouse_cursor=ft.MouseCursor.CLICK,
                                    expand=True,
                                ),
                            ),
                        ),
                    ),
                ).root_component
            )

        background.add_children((
            QItem(
                width_pct=1.0,
                height_pct=0.1,
                anchor=QAnchor(left=0.0, bottom=1.0),
                flets=(
                    control_row := ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        expand=True,
                    ),
                )
            ),
        ))

        control_row.controls.append(close_button)
        control_row.controls.append(check_button)

    def _show_select_dice(self, pres: list[ds.ActionGenerator]) -> None:
        self._prompt_action_layer.clear()
        reveal, background = self._prompt_layer_bg()
        self._prompt_action_layer.add_children((reveal, background))
        background.add_flet_comp((
            prompt_row := ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            make_centre(
                dice_row := ft.Row(
                    expand=True,
                    wrap=True,
                )
            ),
        ))

        selection: dict[ds.Element, int] = defaultdict(int)

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
            pres.append(new_act_gen)
            self._act_gen = pres
            self._on_act_gen_updated()

        choices = pres[-1].choices()
        prompt: list[ds.Element] = []
        requirement: ds.AbstractDice | None = None
        sample_solution: dict[ds.Element, int] | None = None
        if isinstance(choices, ds.AbstractDice):
            if choices.num_dice() == 0:
                check(None)  # type: ignore
                return
            requirement = choices
            for elem in choices:
                for _ in range(choices[elem]):
                    prompt.append(elem)
            choices = self._curr_state.get_player(self._home_pid).dice
            sample_solution = choices.smart_selection(
                requirement,
                self._curr_state.get_player(self._home_pid).characters,
            ).to_dict()
        assert isinstance(choices, ds.ActualDice)

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

        for elem in prompt:
            prompt_row.controls.append(
                QItem(
                    ref_parent=background,
                    height_pct=0.07,
                    width_height_pct=1.0,
                    children=(
                        self._die(elem),
                    ),
                ).root_component
            )
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
                if (
                        sample_solution is not None
                        and elem in sample_solution
                        and sample_solution[elem] > 0
                ):
                    selection_frames[(elem, i)].add_children((
                        QItem(
                            expand=True,
                            border=ft.border.all(5, "#00FF00"),
                        ),
                    ))
                    select_elem(elem)
                    selection_status[(elem, i)] = True
                    sample_solution[elem] -= 1

        def close(_: ft.ControlEvent) -> None:
            assert len(self._act_gen) > 1
            self._act_gen = self._act_gen[:-1]
            self._on_act_gen_updated()

        background.add_children((
            QItem(
                width_pct=1.0,
                height_pct=0.1,
                anchor=QAnchor(left=0.0, bottom=1.0),
                flets=(
                    control_row := ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        expand=True,
                    ),
                )
            ),
        ))
        if len(self._act_gen) > 1:
            control_row.controls.append(
                ft.IconButton(
                    icon=ft.icons.CLOSE,
                    on_click=close,
                    style=self._context.settings.button_style,
                ),
            )
        control_row.controls.append(
            ft.IconButton(
                icon=ft.icons.CHECK,
                on_click=check,
                style=self._context.settings.button_style,
            ),
        )

    def _show_select_static_target(self, pres: list[ds.ActionGenerator]) -> None:
        self._prompt_action_layer.clear()
        reveal, background = self._prompt_layer_bg()
        self._prompt_action_layer.add_children((reveal, background))
        background.add_flet_comp((
            make_centre(
                target_row := ft.Row(
                    expand=True,
                    wrap=True,
                )
            ),
        ))

        choices = pres[-1].choices()
        assert isinstance(choices, tuple) and isinstance(choices[0], ds.StaticTarget)

        last_selection_indicator: QItem | None = None
        selected_target: ds.StaticTarget | None = None

        check_button = ft.IconButton(
            icon=ft.icons.CHECK,
            style=self._context.settings.button_style,
            icon_color="#000000",
        )

        def close(_: ft.ControlEvent) -> None:
            assert len(self._act_gen) > 1
            self._act_gen = self._act_gen[:-1]
            self._on_act_gen_updated()

        def check(_: ft.ControlEvent) -> None:
            last_act_gen = pres[-1]
            try:
                new_act_gen = last_act_gen.choose(selected_target)
            except Exception:
                dlg = ft.AlertDialog(title=ft.Text("Invalid Selection"))
                dlg.open = True
                self._context.page.dialog = dlg
                self._context.page.update()
                return
            pres.append(new_act_gen)
            self._act_gen = pres
            self._on_act_gen_updated()

        def on_clicked(target: ds.StaticTarget, selection_indicator: QItem) -> Callable[[ft.ControlEvent], None]:
            def f(_: ft.ControlEvent) -> None:
                nonlocal last_selection_indicator
                nonlocal selected_target

                selected_target = target
                if last_selection_indicator is selection_indicator:
                    check(None)  # type: ignore
                    return
                if last_selection_indicator is not None:
                    last_selection_indicator.clear()
                last_selection_indicator = selection_indicator
                last_selection_indicator.add_children((
                    QItem(
                        expand=True,
                        border=ft.border.all(5, "#00FF00"),
                    ),
                ))
                if check_button.icon_color == "#000000":
                    check_button.icon_color = "#FFFFFF"
                    check_button.on_click = check
                background.root_component.update()
            return f

        for target in choices:
            name: str
            src_addr: str
            if target.zone is ds.Zone.CHARACTERS:
                char = self._curr_state.get_character_target(target)
                if char is None:
                    continue
                name = char.name()
                src_addr = f"assets/char-cards/{char.name()}.png"
            elif target.zone is ds.Zone.SUMMONS:
                summon_target = self._curr_state.get_target(target)
                if not isinstance(summon_target, ds.Summon):
                    continue
                name = summon_target.__class__.__name__
                src_addr = f"assets/summons/{name.removesuffix('Summon') + 'Card'}.png"
            elif target.zone is ds.Zone.SUPPORTS:
                support_target = self._curr_state.get_target(target)
                if not isinstance(support_target, ds.Support):
                    continue
                name = support_target.__class__.__name__
                src_addr = f"assets/cards/{name.removesuffix('Support') + 'Card'}.png"
            else:
                print(f"ERROR: {target.zone} not catched")
                continue
            target_row.controls.append(
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
                            text=name,
                            text_colour="#000000",
                            size_rel_height=0.1,
                        ),
                        QImage(
                            expand=True,
                            src=src_addr,
                        ),
                        selection_indicator := QItem(
                            expand=True,
                        ),
                        click_pane := QItem(
                            expand=True,
                            flets=(
                                ft.GestureDetector(
                                    on_tap=on_clicked(target, selection_indicator),
                                    mouse_cursor=ft.MouseCursor.CLICK,
                                    expand=True,
                                ),
                            ),
                        ),
                    ),
                ).root_component
            )

        background.add_children((
            QItem(
                width_pct=1.0,
                height_pct=0.1,
                anchor=QAnchor(left=0.0, bottom=1.0),
                flets=(
                    control_row := ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        expand=True,
                    ),
                ),
            ),
        ))
        control_row.controls.append(close_button := ft.IconButton(
            icon=ft.icons.CLOSE,
            on_click=close,
            style=self._context.settings.button_style,
        ))
        control_row.controls.append(check_button)

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
        chars = game_state.get_player(pid).characters
        item.add_flet_comp(ft.Row(
            controls=[
                self._character(item, pid, char.id, game_state).root_component
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
                for i, support in enumerate(game_state.get_player(pid).supports)
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
                for i, summon in enumerate(game_state.get_player(pid).summons)
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
                self._skills(pid, game_state),
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

    def _character(
            self,
            ref_parent: QItem,
            pid: ds.Pid,
            char_id: int,
            game_state: ds.GameState,
    ) -> QItem:
        chars = game_state.get_player(pid).characters
        char = chars.just_get_character(char_id)
        is_active = char.id == chars.get_active_character_id()
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
                                    src=f"assets/char-cards/{char.name()}75.png",
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        )
        if char.is_defeated():
            char_card.add_children((
                QItem(
                    expand=True,
                    colour=ft.colors.with_opacity(0.7, "#000000"),
                ),
            ))
            return item
        if char.hp == 0:
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
            hidden_statuses = char.hidden_statuses
            character_statuses = char.character_statuses
            content = '\n'.join((
                "<Implicit Statuses>",
                '\n'.join([
                    "    - " + s
                    for s in hidden_statuses.dict_str()
                ]),
                "\n<Character Statuses>",
                '\n'.join([
                    "    - " + s
                    for s in character_statuses.dict_str()
                ]),
            ))
            optional_content = ""
            if is_active:
                combat_status = game_state.get_player(pid).combat_statuses
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
                text=f"{char.hp}",
                text_colour="#FFFFFF",
                size_rel_height=0.6,
                rotate=ft.Rotate(angle=-0.25 * pi, alignment=ft.alignment.center),
                width_pct=2.0,
                height_pct=1.0,
                align=QAlign(x_pct=0.5, y_pct=0.5),
            )
        )
        equipments: ds.Statuses = char.character_statuses
        eq_map = {
            dsst.TalentEquipmentStatus: "Talent",
            dsst.WeaponEquipmentStatus: "Weapon",
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
        for energy in range(1, char.max_energy + 1):
            char_card.add_children((
                QItem(
                    height_pct=energy_height,
                    width_height_pct=1.0,
                    align=QAlign(x_pct=1.0, y_pct=(1.5 * energy - 0.5) * energy_height),
                    colour=ft.colors.with_opacity(
                        1, "#EEEE00" if energy <= char.energy else "#A28E75"
                    ),
                    border=ft.border.all(2, "#DBC9AF"),
                    rotate=ft.Rotate(angle=0.25 * pi, alignment=ft.alignment.center),
                )
            ))
        # elem_colour_map = {
        #     ds.Element.PYRO: "#E9683E",
        #     ds.Element.HYDRO: "#4CBBEA",
        #     ds.Element.ANEMO: "#6CBE9F",
        #     ds.Element.ELECTRO: "#A57FB6",
        #     ds.Element.DENDRO: "#9AC546",
        #     ds.Element.CRYO: "#96D1DC",
        #     ds.Element.GEO: "#F6AD43",
        # }
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
                                src=f"assets/elem-icons/{self.ELEM_NAME_MAP[elem]}.png",
                                fit=ft.ImageFit.FILL,
                            )
                        )
                    )[0].root_component
                    for elem in char.elemental_aura
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
        for i, status in enumerate(char.character_statuses):
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
            for i, status in enumerate(game_state.get_player(pid).combat_statuses):
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

    def _dice(
            self,
            pid: ds.Pid,
            game_state: ds.GameState,
    ) -> QItem:
        dice = game_state.get_player(pid).dice
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
                        text=f"{game_state.get_player(pid).deck_cards.num_cards()}",
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
            elif game_state.get_player(self._home_pid).in_end_phase():
                info_row.controls.append(
                    QItem(
                        ref_parent=card_info,
                        height_pct=0.7,
                        width_height_pct=1.0,
                        border=ft.border.all(3, "#ef8132"),
                        border_radius=0x7fffffff,
                        children=(
                            QItem(
                                height=3,
                                width_pct=1.0,
                                align=QAlign(x_pct=0.5, y_pct=0.5),
                                colour="#ef8132",
                                rotate=ft.Rotate(angle=0.25 * pi, alignment=ft.alignment.center),
                            ),
                        ),
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
                        text=f"{game_state.get_player(pid).deck_cards.num_cards()}",
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
            elif game_state.get_player(self._home_pid.other()).in_end_phase():
                info_row.controls.append(
                    QItem(
                        ref_parent=card_info,
                        height_pct=0.7,
                        width_height_pct=1.0,
                        border=ft.border.all(3, "#ef8132"),
                        border_radius=0x7fffffff,
                        children=(
                            QItem(
                                height=3,
                                width_pct=0.5,
                                align=QAlign(x_pct=0.5, y_pct=0.5),
                                colour="#ef8132",
                                rotate=ft.Rotate(angle=0.25 * pi, alignment=ft.alignment.center),
                            ),
                        ),
                    ).root_component
                )
        return item

    _SKILL_STR_MAP: dict[ds.CharacterSkill, str] = {
        ds.CharacterSkill.SKILL1: "I",
        ds.CharacterSkill.SKILL2: "II",
        ds.CharacterSkill.SKILL3: "III",
        ds.CharacterSkill.ELEMENTAL_BURST: "X",
    }

    def _skills(
            self,
            pid: ds.Pid,
            game_state: ds.GameState,
    ) -> QItem:
        item = QItem(
            height_pct=0.5,
            width_pct=1.0,
            anchor=QAnchor(left=0.0, bottom=1.0),
        )
        if pid is not self._home_pid:
            return item
        active_char = game_state.get_player(pid).characters.get_active_character()
        if active_char is None or active_char.is_defeated():
            return item
        item.add_children(QItem(
            height_pct=0.48,
            width_pct=1.0,
            anchor=QAnchor(left=0.0, bottom=1.0),
            flets=(
                skill_row := ft.Row(
                    expand=True,
                    alignment=ft.MainAxisAlignment.END,
                )
            ),
        ))

        # SKILL
        skills = active_char.skills()
        skill_act_gen: list[ds.ActionGenerator] | None = None
        if (
                self._act_gen is not None
                and len(self._act_gen) == 1
                and ds.ActionType.CAST_SKILL in self._act_gen[0].choices()
        ):
            skill_act_gen = [
                self._act_gen[0],
                self._act_gen[0].choose(ds.ActionType.CAST_SKILL),
            ]
            available_skills: tuple[ds.CharacterSkill] = skill_act_gen[-1].choices()
        for skill in skills:
            body = QText(
                ref_parent=item,
                height_pct=0.48,
                width_height_pct=1.0,
                colour="#A87845",
                border=ft.border.all(3, "#DBC9AF"),
                border_radius=0x7fffffff,
                text=self._SKILL_STR_MAP[skill],
                text_colour="#FFFFFF",
                size_rel_height=0.5,
            )
            skill_row.controls.append(body.root_component)

            def choose_skill(skill: ds.CharacterSkill) -> None:
                def f(_: ft.ControlEvent) -> None:
                    next_act_gen = skill_act_gen[-1].choose(skill)
                    self._act_gen.append(next_act_gen)
                    self._on_act_gen_updated()
                return f

            if skill_act_gen is None or skill not in available_skills:
                body.add_children(QItem(
                    expand=True,
                    border_radius=0x7fffffff,
                    colour=ft.colors.with_opacity(0.5, "#000000"),
                ))
            else:
                body.add_flet_comp(ft.GestureDetector(
                    on_tap=choose_skill(skill),
                    mouse_cursor=ft.MouseCursor.CLICK,
                    expand=True,
                    visible=not self._in_history,
                ))

        # SWAP
        item.add_children(
            swap_slot := QText(
                height_pct=0.48,
                width_height_pct=1.0,
                anchor=QAnchor(right=1.0, top=0.0),
                colour="#A87845",
                border=ft.border.all(3, "#DBC9AF"),
                border_radius=0x7fffffff,
                text="⇌",
                text_colour="#FFFFFF",
                size_rel_height=0.5,
                children=(
                    swap_cover := QItem(
                        expand=True,
                    )
                )
            )
        )
        swap_act_gen: list[ds.ActionGenerator] | None = None
        if (
                self._act_gen is not None
                and len(self._act_gen) == 1
                and ds.ActionType.SWAP_CHARACTER in self._act_gen[0].choices()
        ):
            swap_act_gen = [
                self._act_gen[0],
                self._act_gen[0].choose(ds.ActionType.SWAP_CHARACTER),
            ]

        def choose_swap(_: ft.ControlEvent) -> None:
            self._act_gen = swap_act_gen
            self._on_act_gen_updated()

        if swap_act_gen is None:
            swap_cover.add_children(QItem(
                expand=True,
                border_radius=0x7fffffff,
                colour=ft.colors.with_opacity(0.5, "#000000"),
            ))
        else:
            swap_cover.add_flet_comp(ft.GestureDetector(
                on_tap=choose_swap,
                mouse_cursor=ft.MouseCursor.CLICK,
                expand=True,
                visible=not self._in_history,
            ))
        return item

    def _end_round(
            self,
            pid: ds.Pid,
            game_state: ds.GameState,
    ) -> QItem:
        item = QItem(
            height_pct=0.04,
            width_pct=1.0,
            align=QAlign(x_pct=0.5, y_pct=0.43),
            children=(
            ),
        )
        if not isinstance(game_state.phase, game_state.mode.action_phase):
            return item
        item.add_children(
            end_round_frame := QItem(
                height_pct=1.0,
                width_height_pct=1.0,
                anchor=QAnchor(right=1.0, top=0.0),
                colour="#A87845",
                border=ft.border.all(3, "#DBC9AF"),
                border_radius=0x7fffffff,
                children=(
                    QItem(
                        height=3,
                        width_pct=0.5,
                        align=QAlign(x_pct=0.5, y_pct=0.5),
                        colour="#DBC9AF",
                        rotate=ft.Rotate(angle=0.25 * pi, alignment=ft.alignment.center),
                    ),
                ),
            ),
        )
        act_gen = self._base_act_gen
        if (
                not game_state.get_player(pid).in_action_phase()
                or act_gen is None
                or len(self._act_gen) > 1
                or ds.ActionType.END_ROUND not in act_gen.choices()
        ):
            end_round_frame.add_children((
                QItem(
                    expand=True,
                    colour=ft.colors.with_opacity(0.5, "#000000"),
                    border_radius=0x7fffffff,
                ),
            ))
            return item

        def end_round(_: ft.ControlEvent) -> None:
            next_act_gen = act_gen.choose(ds.ActionType.END_ROUND)
            self._act_gen.append(next_act_gen)
            self._on_act_gen_updated()

        end_round_frame.add_flet_comp(ft.GestureDetector(
            on_tap=end_round,
            mouse_cursor=ft.MouseCursor.CLICK,
            expand=True,
            visible=not self._in_history,
        ))
        return item

    def _cards(
            self,
            pid: ds.Pid,
            game_state: ds.GameState,
    ) -> QItem:
        cards = game_state.get_player(pid).hand_cards
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
        def click_card(_: ft.ControlEvent) -> None:
            self._show_select_card()
            self._prompt_action_layer.root_component.update()

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
                QItem(
                    expand=True,
                    flets=(
                        ft.GestureDetector(
                            on_tap=click_card,
                            mouse_cursor=ft.MouseCursor.CLICK,
                            expand=True,
                            visible=pid is self._home_pid,
                        ),
                    ),
                )
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
                    src=f"assets/elem-icons/{self.ELEM_NAME_MAP[elem]}.png",
                    width_pct=0.7,
                    height_pct=0.7,
                    align=QAlign(x_pct=0.5, y_pct=0.5),
                ),
            ),
        )
