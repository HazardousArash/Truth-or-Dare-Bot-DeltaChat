from dataclasses import dataclass, field 
from enum import Enum
from typing import List, Optional, Set
import time

class Gender(Enum):
    BOY = "boy"
    GIRL = "girl"
    BOTH = "both"


class QuestionType(Enum):
    TRUTH = "truth"
    DARE = "dare"


@dataclass
class Question:
    id: int
    text: str
    qtype: QuestionType
    target_gender: Gender


@dataclass
class Player:
    addr: str
    name: str
    gender: Gender

@dataclass
class GameState:
    chat_id: int
    created_by: str

    players: List[Player] = field(default_factory=list)

    started: bool = False

    # Handling turns:
    current_turn_index: int = 0
    current_player_addr: Optional[str] = None

    # question state:
    current_question: Optional[Question] = None
    awaiting_choice: bool = False

    # prevent repeated questions
    used_question_ids: Set[int] = field(default_factory=set)

    # inactivity timeout
    last_activity_ts: float = field(default_factory=time.time)