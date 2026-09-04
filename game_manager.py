import time
from typing import Dict, Optional

from models import GameState, Player, QuestionType, Gender
from config import MAX_PLAYERS, MIN_PLAYERS, INACTIVITY_TIMEOUT, ALLOWED_ENDERS
from question_bank import QuestionBank
from messages import Messages

class GameManager:

    def __init__(self, question_bank: QuestionBank):
        self.games: Dict[int, GameState] = {}
        self.question_bank = question_bank

    def get_game(self, chat_id: int) -> Optional[GameState]:
        return self.games.get(chat_id)

    def create_game(self, chat_id: int, creator_addr: str) -> str:

        if chat_id in self.games:
            return Messages["game_already_running"]

        game = GameState(
            chat_id=chat_id,
            created_by=creator_addr
        )

        self.games[chat_id] = game

        return Messages["game_created"]


    def join_player(self, chat_id: int, addr: str, name: str, gender: Gender) -> str:

        game = self.get_game(chat_id)

        if not game:
            return Messages["no_active_games"]

        if game.started:
            return Messages["game_already_started_cannot_enter"]

        if len(game.players) >= MAX_PLAYERS:
            return Messages["max_player_reached"]

        for p in game.players:
            if p.addr == addr:
                return Messages["you_already_joined"]

        player = Player(
            addr=addr,
            name=name,
            gender=gender
        )

        game.players.append(player)

        game.last_activity_ts = time.time()

        return f"{name} {Messages['added_to_game']}"


    def start_game(self, chat_id: int, addr: str) -> str:

        game = self.get_game(chat_id)

        if not game:
            return Messages["no_active_games"]

        if addr != game.created_by:
            return Messages["only_creator_can_start"]

        if len(game.players) < MIN_PLAYERS:
            return Messages["not_enough_players"]

        game.started = True
        game.current_turn_index = 0
        game.current_player_addr = game.players[0].addr
        game.awaiting_choice = True

        game.last_activity_ts = time.time()

        player = game.players[0]

        return (
            f"{Messages['game_started']}!\n"
            f"{Messages['your_turn']} {player.name}\n"
            f"{Messages['truth_or_dare']}"
        )

    def get_current_player(self, chat_id: int) -> Optional[Player]:

        game = self.get_game(chat_id)

        if not game or not game.players:
            return None

        return game.players[game.current_turn_index]


    def choose_question(self, chat_id: int, qtype: QuestionType) -> str:

        game = self.get_game(chat_id)

        if not game:
            return Messages["game_not_active"]

        player = self.get_current_player(chat_id)

        question = self.question_bank.get_random_question(
            qtype=qtype,
            player_gender=player.gender,
            used_ids=game.used_question_ids
        )

        if not question:
            self.end_game(chat_id)
            return Messages["questions_finished"]


        game.used_question_ids.add(question.id)

        game.current_question = question
        game.awaiting_choice = False

        game.last_activity_ts = time.time()

        return f"{player.name}:\n{question.text}"



    def next_turn(self, chat_id: int) -> str:

        game = self.get_game(chat_id)

        if not game:
            return Messages["game_not_active"]

        game.current_turn_index += 1

        if game.current_turn_index >= len(game.players):
            game.current_turn_index = 0

        player = game.players[game.current_turn_index]

        game.current_player_addr = player.addr
        game.awaiting_choice = True
        game.current_question = None

        game.last_activity_ts = time.time()

        return (
            f"{Messages['your_turn']} {player.name}\n"
            f"{Messages['truth_or_dare']}"
        )

    def end_game(self, chat_id: int):

        if chat_id in self.games:
            del self.games[chat_id]


    def try_end_by_user(self, chat_id: int, addr: str) -> str:

        game = self.get_game(chat_id)

        if not game:
            return Messages["no_active_games"]

        if (
            addr != game.created_by
            and addr not in ALLOWED_ENDERS
        ):
            return Messages["cannot_end_game"]

        self.end_game(chat_id)

        return Messages["game_ended"]


    def check_timeout(self, chat_id: int) -> Optional[str]:

        game = self.get_game(chat_id)

        if not game:
            return None

        now = time.time()

        if now - game.last_activity_ts > INACTIVITY_TIMEOUT:
            self.end_game(chat_id)
            return Messages["timeout"]

        return None