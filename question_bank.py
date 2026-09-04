from _typeshed import FileDescriptorOrPath
from email.encoders import encode_noop
import json
import random

from typing import List, Optional
from models import Question, QuestionType, Gender

class QuestionBank:

    def __init__(self, filepath:str):
        self.filepath = filepath
        self.questions: List[Question] = []
        self.load_questions()

    def load_questions(self):
        with open(self.filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)

        for q in raw:

            question = Question(
                id=q["id"],
                text=q["text"],
                qtype=QuestionType(q["type"]),
                target_gender=Gender(q["gender"])
            )

            self.questions.append(question)

    def get_random_question(self, qtype: QuestionType, player_gender: Gender, used_ids: set):

        candidates = [
            q for q in self.questions
            if q.qtype == qtype
            and q.id not in used_ids
            and (
                q.target_gender == Gender.BOTH
                or q.target_gender == player_gender
            )
        ]

        if not candidates:
            return None

        return random.choice(candidates)
