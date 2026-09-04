from deltachat import Bot, Message
import time

from config import BOT_EMAIL, BOT_PASSWORD, QUESTIONS_FILE
from commands import COMMANDS
from models import Gender, QuestionType
from question_bank import QuestionBank
from game_manager import GameManager
from admin import AdminManager

# INIT CORE SYSTEMS
question_bank = QuestionBank(QUESTIONS_FILE)
game_manager = GameManager(question_bank)
admin_manager = AdminManager(question_bank)

# INIT DELTACHAT RPC CLIENT
dc = DeltaChat()

account = dc.add_account({
    "addr": BOT_EMAIL,
    "mail_pw": BOT_PASSWORD
})

account.start_io()

# HELPERS
def normalize(text: str) -> str:
    return text.strip().lower()


def send(chat_id, text):
    account.send_text(chat_id, text)


# MAIN EVENT LOOP

print("Bot is running...")

while True:

    events = dc.get_next_events()

    for event in events:

        try:

            # only new messages
            if event["kind"] != "IncomingMsg":
                continue

            msg_id = event["msg_id"]

            msg = account.get_message_by_id(msg_id)

            # no self messages
            if msg.is_outgoing():
                continue

            chat = msg.chat
            chat_id = chat.id

            sender = msg.get_sender_contact()

            addr = sender.addr
            name = sender.display_name or "بازیکن"

            text = normalize(msg.text or "")

            # TIMEOUT CHECK
            timeout_msg = game_manager.check_timeout(chat_id)
            if timeout_msg:
                send(chat_id, timeout_msg)

            # detect private chat
            is_private = chat.is_contact_request()

            if is_private:

                # start admin login
                if addr not in admin_manager.sessions:
                    send(chat_id, admin_manager.start_auth(addr))
                    continue

                # continue auth steps
                if not admin_manager.is_admin(addr):
                    response = admin_manager.handle_auth(addr, text)
                    if response:
                        send(chat_id, response)
                    continue

            # CREATE GAME
            if text == COMMANDS["create"]:

                response = game_manager.create_game(
                    chat_id,
                    addr
                )

                send(chat_id, response)
                continue

            # JOIN BOY
            if text == COMMANDS["join_boy"]:

                response = game_manager.join_player(
                    chat_id=chat_id,
                    addr=addr,
                    name=name,
                    gender=Gender.BOY
                )

                send(chat_id, response)
                continue

            # JOIN GIRL
            if text == COMMANDS["join_girl"]:

                response = game_manager.join_player(
                    chat_id=chat_id,
                    addr=addr,
                    name=name,
                    gender=Gender.GIRL
                )

                send(chat_id, response)
                continue

            # START GAME
            if text == COMMANDS["start"]:

                response = game_manager.start_game(
                    chat_id,
                    addr
                )

                send(chat_id, response)
                continue

            # TRUTH
            if text == COMMANDS["truth"]:

                response = game_manager.choose_question(
                    chat_id,
                    QuestionType.TRUTH
                )

                send(chat_id, response)
                continue

            # DARE
            if text == COMMANDS["dare"]:

                response = game_manager.choose_question(
                    chat_id,
                    QuestionType.DARE
                )

                send(chat_id, response)
                continue

            # NEXT TURN
            if text == COMMANDS["next"]:

                response = game_manager.next_turn(chat_id)

                send(chat_id, response)
                continue

            # END GAME
            if text == COMMANDS["end"]:

                response = game_manager.try_end_by_user(
                    chat_id,
                    addr
                )

                send(chat_id, response)
                continue

        except Exception as e:

            print("ERROR:", e)

    time.sleep(1)