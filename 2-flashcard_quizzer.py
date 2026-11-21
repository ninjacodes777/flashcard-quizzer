#!/usr/bin/env python3
"""flashcard-quizzer - a tiny terminal flashcard app.

Decks live as JSON files in the `decks/` folder. Each deck is a list of
cards, and every card has a "front" (the question) and a "back" (the
answer). A quiz round shuffles the cards, shows you one front at a time,
lets you reveal the back when you are ready, and asks whether you got it
right. At the end you get a score summary and the option to retry only
the cards you missed.

Everything here uses only the Python standard library.
"""

import json
import random
import sys
from pathlib import Path

# Decks are looked up relative to this file, so the app works no matter
# which folder you run it from.
DECKS_DIR = Path(__file__).resolve().parent / "decks"


# ---------------------------------------------------------------------------
# Loading decks (data persistence: JSON files on disk -> Python objects)
# ---------------------------------------------------------------------------

def load_deck(path):
    """Read one deck file and return it as a dictionary.

    A deck file looks like this:

        {
            "name": "Python Basics",
            "cards": [
                {"front": "What keyword defines a function?", "back": "def"},
                ...
            ]
        }
    """
    with open(path, "r", encoding="utf-8") as f:
        deck = json.load(f)

    # Basic validation so a broken deck file fails with a clear message.
    if "cards" not in deck or not deck["cards"]:
        raise ValueError(f"{path.name}: deck has no cards")
    for card in deck["cards"]:
        if "front" not in card or "back" not in card:
            raise ValueError(f"{path.name}: every card needs a front and a back")

    deck.setdefault("name", path.stem)
    return deck


def find_decks():
    """Return a sorted list of every .json deck file in the decks folder."""
    if not DECKS_DIR.is_dir():
        return []
    return sorted(DECKS_DIR.glob("*.json"))


# ---------------------------------------------------------------------------
# The quiz itself
# ---------------------------------------------------------------------------

def ask(prompt, valid):
    """Ask until the user types one of the valid answers (lowercase)."""
    while True:
        answer = input(prompt).strip().lower()
        if answer in valid:
            return answer
        print(f"  Please type one of: {', '.join(sorted(valid))}")


def play_round(cards, title):
    """Play one round over `cards` (already shuffled).

    Returns the list of cards the user marked as wrong, so the caller can
    offer a retry round with just those cards.
    """
    wrong = []
    total = len(cards)

    print(f"\n=== {title} ({total} cards) ===")
    print("Press Enter to reveal the answer, then mark yourself y (right) or n (wrong).")

    for i, card in enumerate(cards, start=1):
        print(f"\nCard {i}/{total}")
        print(f"  Q: {card['front']}")
        input("  ... press Enter to reveal ...")
        print(f"  A: {card['back']}")

        got_it = ask("  Did you get it right? (y/n) ", {"y", "n"})
        if got_it == "n":
            wrong.append(card)

    right = total - len(wrong)
    percent = round(100 * right / total)
    print("\n--- Round over ---")
    print(f"  Right: {right}/{total} ({percent}%)")
    print(f"  Wrong: {len(wrong)}/{total}")

    return wrong


def quiz(deck):
    """Run full rounds of a deck, offering retry rounds for missed cards."""
    # random.shuffle works in place, so work on a copy of the deck's list.
    cards = deck["cards"][:]
    round_number = 1

    while True:
        random.shuffle(cards)
        title = deck["name"] if round_number == 1 else f"{deck['name']} (retry round {round_number})"
        wrong = play_round(cards, title)

        if not wrong:
            print("\nPerfect round - nothing left to retry. Nice work!")
            return

        again = ask(f"\nRetry the {len(wrong)} card(s) you missed? (y/n) ", {"y", "n"})
        if again == "n":
            print("Good session - come back soon!")
            return

        cards = wrong
        round_number += 1


# ---------------------------------------------------------------------------
# Menu and command-line handling
# ---------------------------------------------------------------------------

def list_decks():
    """Print every available deck with its card count."""
    paths = find_decks()
    if not paths:
        print(f"No decks found in {DECKS_DIR}")
        print("Add a .json file there - see README.md for the format.")
        return

    print("Available decks:")
    for path in paths:
        try:
            deck = load_deck(path)
            print(f"  {path.stem:<20} {deck['name']} ({len(deck['cards'])} cards)")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"  {path.stem:<20} (broken file: {e})")


def choose_deck_interactively():
    """Show the decks and let the user pick one by number."""
    paths = find_decks()
    if not paths:
        print(f"No decks found in {DECKS_DIR}")
        print("Add a .json file there - see README.md for the format.")
        return None

    print("Pick a deck:")
    for i, path in enumerate(paths, start=1):
        try:
            deck = load_deck(path)
            print(f"  {i}. {deck['name']} ({len(deck['cards'])} cards)")
        except (ValueError, json.JSONDecodeError):
            print(f"  {i}. {path.stem} (broken file)")

    while True:
        choice = input("\nDeck number (or q to quit): ").strip().lower()
        if choice == "q":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(paths):
            return load_deck(paths[int(choice) - 1])
        print("  Please enter a number from the list, or q.")


def main(argv):
    # `python flashcard_quizzer.py decks` -> list decks and exit.
    if len(argv) == 2 and argv[1] == "decks":
        list_decks()
        return

    # `python flashcard_quizzer.py quiz <deck-name>` -> quiz one deck directly.
    if len(argv) == 3 and argv[1] == "quiz":
        path = DECKS_DIR / f"{argv[2]}.json"
        if not path.is_file():
            print(f"No deck named '{argv[2]}'. Available decks:")
            list_decks()
            sys.exit(1)
        quiz(load_deck(path))
        return

    # `python flashcard_quizzer.py` with no arguments -> interactive menu.
    if len(argv) == 1:
        print("Welcome to flashcard-quizzer!")
        deck = choose_deck_interactively()
        if deck is not None:
            quiz(deck)
        return

    # Anything else -> show how to use the app.
    print(__doc__)


if __name__ == "__main__":
    try:
        main(sys.argv)
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C or Ctrl+D should exit quietly instead of dumping a traceback.
        print("\nBye!")
