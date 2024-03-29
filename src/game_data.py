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
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Literal

from typing_extensions import Self

import dgisim as ds
from dgisim import agents as dsa
from dgisim import card as dscd
from dgisim import status as dsst
from dgisim import summon as dssm
from dgisim import support as dssp

__all__ = [
    "PlayerSettings",
    "GamePlaySettings",
    "Match",
    "GameData",
    "GameDataListener",
]


@dataclass(kw_only=True)
class PlayerSettings:
    player_type: Literal["P", "E"]
    random_deck: bool = False

    def as_tuple(self) -> tuple[str, bool]:
        return (self.player_type, self.random_deck)


@dataclass(kw_only=True)
class GamePlaySettings:
    primary_player: ds.Pid
    primary_settings: PlayerSettings
    oppo_settings: PlayerSettings
    local: bool

    @classmethod
    def from_random_PVE(cls) -> None:
        return GamePlaySettings(
            primary_player=ds.Pid.P1,
            primary_settings=PlayerSettings(player_type="P", random_deck=True),
            oppo_settings=PlayerSettings(player_type="E", random_deck=True),
            local=True,
        )

    @classmethod
    def from_random_local_PVP(cls) -> None:
        return GamePlaySettings(
            primary_player=ds.Pid.P1,
            primary_settings=PlayerSettings(player_type="P", random_deck=True),
            oppo_settings=PlayerSettings(player_type="P", random_deck=True),
            local=True,
        )

    @classmethod
    def from_random_EVE(cls) -> None:
        return GamePlaySettings(
            primary_player=ds.Pid.P1,
            primary_settings=PlayerSettings(player_type="E", random_deck=True),
            oppo_settings=PlayerSettings(player_type="E", random_deck=True),
            local=True,
        )

    def setting_of(self, pid: ds.Pid) -> PlayerSettings:
        if pid is self.primary_player:
            return self.primary_settings
        else:
            return self.oppo_settings

    def as_tuple(self) -> tuple[ds.Pid, tuple[str, bool], tuple[str, bool]]:
        return (
            self.primary_player,
            self.primary_settings.as_tuple(),
            self.oppo_settings.as_tuple(),
        )


@dataclass(kw_only=True)
class MatchNode:
    depth: int = 0
    parent: Self | None = None
    inter_states: list[ds.GameState] = field(default_factory=list)
    stop_state: ds.GameState | None = None
    action: ds.PlayerAction | None = None
    inter_fork: bool = False
    children: list[Self] = field(default_factory=list)

    def is_terminal(self) -> bool:
        return self.stop_state is not None and self.stop_state.game_end()

    def latest_state(self) -> ds.GameState:
        if self.inter_fork:
            return self.inter_states[-1]
        return self.stop_state

    def is_state_complete(self) -> bool:
        return self.inter_fork or self.stop_state is not None


class Match:
    def __init__(
            self,
            initial_state: ds.GameState | None = None,
            agent1: ds.PlayerAgent = dsa.RandomAgent(),
            agent2: ds.PlayerAgent = dsa.RandomAgent(),
    ) -> None:
        self._agent1 = agent1
        self._agent2 = agent2

        if initial_state is None:
            # TODO: init game state according to settings
            initial_state = ds.GameState.from_default()

        if initial_state.waiting_for() is None:
            self._root_match_node = MatchNode(inter_states=[initial_state])
            self._auto_complete_matchnode(self._root_match_node)
        else:
            self._root_match_node = MatchNode(stop_state=initial_state)

        self._curr_match_node = self._root_match_node
        self._focused_index = -1

    @property
    def curr_node(self) -> MatchNode:
        return self._curr_match_node
    
    def new_node(self, init_state: ds.GameState) -> None:
        new_node = MatchNode(
            depth=self._curr_match_node.depth + 1,
            parent=self._curr_match_node,
            inter_states=[init_state],
        )
        self._auto_complete_matchnode(new_node)
        self._curr_match_node.children.append(new_node)
        self._curr_match_node = new_node

    tmp = True

    def _auto_complete_matchnode(self, node: MatchNode) -> None:
        if node.is_state_complete():
            return
        gsm = ds.GameStateMachine(node.inter_states[-1], self._agent1, self._agent2)
        # # Fake Death Swap
        # es = gsm.get_game_state().get_effect_stack()
        # from dgisim import effect as dsef
        # if any(
        #         (
        #             isinstance(e, dsef.CastSkillEffect)
        #             and e.target.pid is ds.Pid.P2
        #         )
        #         for e in es._effects
        # ):
        #     gsm.step_until_holds(
        #         lambda gs: (
        #             (es := gs.get_effect_stack()).is_not_empty()
        #             and isinstance(es.peek(), dsef.AliveMarkCheckerEffect)
        #         )
        #     )
        #     gsm._history[-1] = gsm._history[-1].factory().f_effect_stack(
        #         lambda es: es.push_one(dsef.ReferredDamageEffect(
        #             source=ds.StaticTarget.from_support(ds.Pid.P2, 1),
        #             target=ds.DynamicCharacterTarget.OPPO_ACTIVE,
        #             element=ds.Element.PIERCING,
        #             damage=100,
        #             damage_type=ds.DamageType(status=True, no_boost=True),
        #         ))
        #     ).build()
        #     gsm._game_state = gsm._history[-1]
        gsm.auto_step()
        node.inter_states = gsm.get_history()[:-1]
        node.stop_state = gsm.get_history()[-1]

        # from dgisim import char as dscr
        # if dscr.Dehya not in node.stop_state.get_player1().get_characters():
        #     node.stop_state = node.stop_state.factory().f_player1(
        #         lambda p1: p1.factory().f_characters(
        #             lambda chs: chs.factory().f_character(
        #                 2,
        #                 lambda: dscr.Dehya.from_default(2)
        #             ).build()
        #         ).build()
        #     ).build()

        # temporary add card
        # from dgisim import card as dscd
        # if dscd.BlessingOfTheDivineRelicsInstallation not in node.stop_state.player1.hand_cards:
        #     node.stop_state = node.stop_state.factory().f_player1(
        #         lambda p1: p1.factory().f_hand_cards(
        #             lambda hcs: hcs.add(
        #                 dscd.BlessingOfTheDivineRelicsInstallation
        #             ).add(
        #                 dscd.GildedDreams
        #             )
        #         ).build()
        #     ).build()

        # from dgisim import summon as dssm
        # if dssm.ShadowswordGallopingFrostSummon not in node.stop_state.get_player2().get_summons() and self.tmp:
        #     node.stop_state = node.stop_state.factory().f_player2(
        #         lambda p2: p2.factory().f_summons(
        #             lambda sms: sms.update_summon(
        #                 dssm.ShadowswordGallopingFrostSummon()
        #             ).update_summon(
        #                 dssm.ShadowswordLoneGaleSummon()
        #             ).update_summon(
        #                 dssm.BurningFlameSummon()
        #             ).update_summon(
        #                 dssm.ReflectionSummon()
        #             )
        #         ).build()
        #     ).build()
        #     self.tmp = False

    def agent(self, pid: ds.Pid) -> ds.PlayerAgent:
        if pid is ds.Pid.P1:
            return self._agent1
        else:
            return self._agent2

    def agent_action_step(self, pid: ds.Pid) -> None:
        assert (
            self._curr_match_node.stop_state is not None
            and self._curr_match_node.stop_state.waiting_for() is pid
        )
        agent = self.agent(pid)
        try:
            action = agent.choose_action([self._curr_match_node.stop_state], pid)
        except Exception as e:
            print("Agent cannot provide a valid action:", e)
            return
        print(f"{pid} taking action: {action}")
        self._curr_match_node.action = action
        try:
            next_state = self._curr_match_node.stop_state.action_step(pid, action)
            assert next_state is not None
        except Exception as e:
            print(e)
            return
        self.new_node(next_state)

    def latest_state(self) -> ds.GameState:
        return self._curr_match_node.latest_state()

    def curr_state(self) -> ds.GameState:
        if self._focused_index == -1:
            return self.latest_state()
        else:
            return self._curr_match_node.inter_states[self._focused_index]

    def is_at_latest(self) -> bool:
        return (
            len(self._curr_match_node.children) == 0
            and self.curr_state() is self._curr_match_node.latest_state()
        )

    def action_back(self) -> None:
        curr_node = self._curr_match_node
        if curr_node.parent is None:
            return
        self._curr_match_node = curr_node.parent
        self._focused_index = -1

    def action_forward(self) -> None:
        if len(self._curr_match_node.children) == 0:
            self._focused_index = -1
            return
        self._curr_match_node = self._curr_match_node.children[0]
        self._focused_index = -1

    def step_back(self) -> None:
        if self._focused_index == -1:
            self._focused_index = len(self._curr_match_node.inter_states) - 1
            if self._focused_index == -1:
                self.action_back()
        elif self._focused_index > 0:
            self._focused_index -= 1
        elif self._focused_index == 0:
            if self._curr_match_node.parent is not None:
                self.action_back()
                self._focused_index = -1

    def step_forward(self) -> None:
        if self._focused_index == -1:
            if len(self._curr_match_node.children) != 0:
                self.action_forward()
                if self._curr_match_node.inter_states:
                    self._focused_index = 0
        elif self._focused_index < len(self._curr_match_node.inter_states) - 1:
            self._focused_index += 1
        elif self._focused_index == len(self._curr_match_node.inter_states) - 1:
            self._focused_index = -1

    def curr_state_index(self) -> tuple[int, int]:
        return (
            self._curr_match_node.depth,
            self._focused_index if self._focused_index != -1 else len(self._curr_match_node.inter_states),
        )

GameDataGenre = Literal["latest", "history"]

class GameData:
    def __init__(self) -> None:
        self.curr_game_mode: GamePlaySettings | None = None
        self.matches: dict[tuple, Match] = {}
        self.genred_listeners: dict[GameDataGenre, list[GameDataListener]] = {}

    def init_game(self) -> None:
        """
        Called to initialize or resume a match under the current game mode.
        """
        curr_mode_tuple = self.curr_game_mode.as_tuple()
        if (
                curr_mode_tuple not in self.matches
                or self.matches[curr_mode_tuple].curr_node.is_terminal()
        ):
            self.matches[curr_mode_tuple] = Match()
        self.curr_match = self.matches[curr_mode_tuple]
        self._try_auto_step()

    def take_action(self, pid: ds.Pid, action: ds.PlayerAction) -> None:
        """
        Execuate action and update the current match node.
        """
        assert self._require_action(pid)
        print(f"{pid} taking action: {action}")
        self.curr_match.curr_node.action = action
        try:
            next_state = self.curr_match.curr_node.latest_state().action_step(pid, action)
            assert next_state is not None
        except Exception as e:
            print(e)
            return
        self.curr_match.new_node(next_state)
        self._try_auto_step()

    def surrender(self, pid: ds.Pid) -> None:
        self.curr_match.new_node(
            self.curr_match.curr_node.latest_state().factory().f_phase(
                lambda mode: mode.game_end_phase()
            ).f_player(
                pid,
                lambda p: p.factory().f_characters(
                    lambda cs: cs.factory().f_characters(
                        lambda chs: tuple([
                            char.factory().alive(False).build()
                            for char in chs
                        ])
                    ).build()
                ).build()
            ).build()
        )

    def _try_auto_step(self) -> None:
        waiting_for = self.curr_match.curr_node.latest_state().waiting_for()
        assert waiting_for is not None
        player_settings = self.curr_game_mode.setting_of(waiting_for)
        if player_settings.player_type == "E":
            self.curr_match.agent_action_step(waiting_for)
            self._try_auto_step()
        else:
            self.notify_listeners("latest")

    def _require_action(self, perspective: ds.Pid) -> bool:
        return self.curr_match.curr_state().waiting_for() is perspective

    def curr_game_state(self, perspective: ds.Pid) -> ds.GameState:
        return self.curr_match.curr_state().prespective_view(perspective)

    def action_taken_at_curr(self, perspective: ds.Pid) -> ds.PlayerAction | None:
        if (
                self.curr_match.curr_node.action is None
                or self.curr_match.curr_state() is not self.curr_match.latest_state()
        ):
            return None
        return self.curr_match.curr_node.action  # TODO: perspective

    def is_at_latest(self) -> bool:
        return self.curr_match.is_at_latest()

    def action_back(self) -> None:
        self.curr_match.action_back()

    def action_forward(self) -> None:
        self.curr_match.action_forward()

    def step_back(self) -> None:
        self.curr_match.step_back()

    def step_forward(self) -> None:
        self.curr_match.step_forward()

    def curr_state_index(self) -> tuple[int, int]:
        return self.curr_match.curr_state_index()

    def new_listener(self) -> GameDataListener:
        listener = GameDataListener(self, "latest")
        return listener

    def listener_unsubscribe(self, listener: GameDataListener, genre: GameDataGenre) -> None:
        self.genred_listeners[genre].remove(listener)

    def listener_subscribe(self, listener: GameDataListener, genre: GameDataGenre) -> None:
        if genre not in self.genred_listeners:
            self.genred_listeners[genre] = []
        self.genred_listeners[genre].append(listener)
    
    def notify_listeners(self, genre: GameDataGenre) -> None:
        if genre not in self.genred_listeners:
            return
        for listener in self.genred_listeners[genre]:
            listener.on_update()

class GameDataListener:
    def __init__(self, game_data: GameData, genre: GameDataGenre = "latest") -> None:
        self._game_data = game_data
        self.on_update: Callable[[], None] = lambda: None
        self._genre = genre
        game_data.listener_subscribe(self, genre)

    def set_subscription(self, genre: GameDataGenre) -> None:
        if self._genre == genre:
            return
        self._game_data.listener_unsubscribe(self, self._genre)
        self._genre = genre
        self._game_data.listener_subscribe(self, self._genre)

    def unsubscribe(self) -> None:
        self._game_data.listener_unsubscribe(self, self._genre)
