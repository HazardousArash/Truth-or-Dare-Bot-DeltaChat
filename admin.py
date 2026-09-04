import hashlib


ADMIN_ADDR = ""
BIRTHDAY = ""

SECRET_HASH = ""


class AdminManager:

    def __init__(self, question_bank):

        # question bank object reference
        self.qb = question_bank

        # store per-user auth states
        self.sessions = {}

    def start_auth(self, user_addr):
        """
        Called when admin sends first message in PV.
        Initializes authentication flow.
        """
        self.sessions[user_addr] = {
            "step": 1,
            "authorized": False
        }

        return "Enter your email"

    def handle_auth(self, user_addr, text):
        """
        Handles multi-step authentication.
        """
        session = self.sessions.get(user_addr)
        if not session:
            return None

        step = session["step"]

        # ---- STEP 1: EMAIL ----
        if step == 1:
            if text == ADMIN_ADDR:
                session["step"] = 2
                return "Birthday?"
            return "Wrong"


        # ---- STEP 2: BIRTHDAY ----
        if step == 2:
            if text == BIRTHDAY:
                session["step"] = 3
                return "Today's date?"
            return "Wrong"


        # ---- STEP 3: TODAY'S DATE ----
        if step == 3:
            session["today"] = text
            session["step"] = 4
            return "Enter security key"


        # ---- STEP 4: SECRET KEY ----
        if step == 4:
            hashed_input = hashlib.sha256(text.encode()).hexdigest()

            if hashed_input == SECRET_HASH:
                session["authorized"] = True
                return "Admin access granted"
            return "Wrong key"

    def is_admin(self, user_addr):
        session = self.sessions.get(user_addr)
        return session and session.get("authorized", False)


    def add_question(self, user_addr, question):
        if not self.is_admin(user_addr):
            return "Unauthorized"

        self.qb.add_question(question)
        return "Question added"

    def list_questions(self, user_addr):
        if not self.is_admin(user_addr):
            return "Unauthorized"

        questions = self.qb.get_all()
        lines = []

        for idx, q in enumerate(questions):
            lines.append(f"{idx} - {q}")

        if not lines:
            return "No questions found."

        return "\n".join(lines)

    def remove_question(self, user_addr, index):
        if not self.is_admin(user_addr):
            return "Unauthorized"

        try:
            idx = int(index)
            self.qb.remove_question(idx)
            return "Removed"
        except:
            return "Invalid index"