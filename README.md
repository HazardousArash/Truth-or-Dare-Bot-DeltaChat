# DeltaChat Truth or Dare Bot

DeltaChat Truth or Dare is a multiplayer bot designed to bring the classic game to group chats, featuring turn management, gender-specific routing, and an interactive admin panel.

## Features

*   **Multiplayer Support**: Handles sessions ranging from 2 to 10 players.
*   **Gender-Aware Questions**: Filters prompts dynamically based on whether the player joined as a boy or girl.
*   **Anti-Repetition Engine**: Tracks used IDs to ensure players never see the same question twice in a single session.
*   **Inactivity Timeout**: Automatically clears dormant games after 7 minutes (420 seconds) to free up memory.
*   **Admin Authentication**: Protects moderation commands via a multi-step private message challenge (Email, Birthday, Date, Hash Key).

## User Commands

Players use the following Persian commands in the chat to interact with the bot:

| Command | Action |
| :--- | :--- |
| `بازیساخت` | Creates a new game instance. |
| `بازیپسر` | Joins the current game as a male player. |
| `بازیدختر` | Joins the current game as a female player. |
| `بازیشروع` | Starts the game (restricted to the game creator). |
| `بازیحقیقت` | Selects a Truth question for the current turn. |
| `بازیجرئت` | Selects a Dare question for the current turn. |
| `بازیبعدی` | Passes the turn to the next player. |
| `بازیپایان` | Ends the game immediately. |

## Codebase Architecture

*   **`bot.py`**: The core entry point that initializes the DeltaChat RPC client, listens for incoming messages, and routes events.
*   **`game_manager.py`**: Manages concurrent `GameState` objects, player joining, turn advancement, and timeouts.
*   **`question_bank.py`**: Parses the underlying JSON file, mapping raw data to `Question` objects and handling random selection.
*   **`admin.py`**: Manages the four-step admin authentication flow and exposes functions to add, list, or remove questions.
*   **`models.py`**: Defines standard dataclasses (`Player`, `GameState`, `Question`) and enums (`Gender`, `QuestionType`).
*   **`messages.py`**: Consolidates all Persian system messages and alerts sent by the bot.
*   **`commands.py`**: Houses the dictionary mapping of trigger words.
*   **`config.py`**: Stores global constraints, admin email addresses, and the target file name for questions.

## Creating the Question Bank JSON

The bot loads prompts from a JSON array processed by `question_bank.py`. The file must be structured as a list of objects containing specific keys mapped to the internal data models. 

Ensure your JSON file follows this structure:

```json
[
  {
    "id": 1,
    "text": "What is your biggest fear?",
    "type": "truth",
    "gender": "both"
  },
  {
    "id": 2,
    "text": "Do 10 pushups.",
    "type": "dare",
    "gender": "boy"
  },
  {
    "id": 3,
    "text": "Let the group style your hair.",
    "type": "dare",
    "gender": "girl"
  }
]
```
