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
    type: Literal["P", "E"]
    random_deck: bool = False

    def as_tuple(self) -> tuple[str, bool]:
        return (self.type, self.random_deck)


@dataclass(kw_only=True)
class GamePlaySettings:
    primary_player: ds.Pid
    primary_settings: PlayerSettings
    oppo_settings: PlayerSettings
    # completely_random: bool = False

    @classmethod
    def from_random_PVE(cls) -> None:
        return GamePlaySettings(
            primary_player=ds.Pid.P1,
            primary_settings=PlayerSettings(type="P", random_deck=True),
            oppo_settings=PlayerSettings(type="E", random_deck=True),
            # completely_random=True,
        )

    @classmethod
    def from_random_EVE(cls) -> None:
        return GamePlaySettings(
            primary_player=ds.Pid.P1,
            primary_settings=PlayerSettings(type="E", random_deck=True),
            oppo_settings=PlayerSettings(type="E", random_deck=True),
            # completely_random=True,
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
        self._curr_match_node = new_node

    def _auto_complete_matchnode(self, node: MatchNode) -> None:
        if node.is_state_complete():
            return
        gsm = ds.GameStateMachine(node.inter_states[-1], self._agent1, self._agent2)
        gsm.auto_step()
        node.inter_states = gsm.get_history()[:-1]
        node.stop_state = gsm.get_history()[-1]

        # from dgisim import card as dscd
        # if dscd.KnightsOfFavoniusLibrary not in node.stop_state.get_player1().get_hand_cards():
        #     node.stop_state = node.stop_state.factory().f_player1(
        #         lambda p1: p1.factory().f_hand_cards(
        #             lambda hcs: hcs.add(dscd.KnightsOfFavoniusLibrary)
        #         ).build()
        #     ).build()

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
        else:
            # TODO: remove
            self.matches[curr_mode_tuple] = Match()
        self.curr_match = self.matches[curr_mode_tuple]
        self.try_auto_step()

    def take_action(self, pid: ds.Pid, action: ds.PlayerAction) -> None:
        """
        Execuate action and update the current match node.
        """
        assert self.require_action(pid)
        print(f"{pid} taking action: {action}")
        self.curr_match.curr_node.action = action
        try:
            next_state = self.curr_match.curr_node.latest_state().action_step(pid, action)
            assert next_state is not None
        except Exception as e:
            print(e)
            return
        self.curr_match.new_node(next_state)
        self.try_auto_step()

    def try_auto_step(self) -> None:
        waiting_for = self.curr_match.curr_node.latest_state().waiting_for()
        assert waiting_for is not None
        player_settings = self.curr_game_mode.setting_of(waiting_for)
        if player_settings.type == "E":
            self.curr_match.agent_action_step(waiting_for)
            self.try_auto_step()
        else:
            self.notify_listeners("latest")

    def require_action(self, perspective: ds.Pid) -> bool:
        return self.curr_match.curr_node.latest_state().waiting_for() is perspective

    def curr_game_state(self, perspective: ds.Pid) -> ds.GameState:
        return self.curr_match.curr_node.latest_state().prespective_view(perspective)

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
