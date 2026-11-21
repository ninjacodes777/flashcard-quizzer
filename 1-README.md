# flashcard-quizzer

A simple terminal flashcard app written in Python. Load a deck of flashcards,
quiz yourself card by card, and retry only the ones you got wrong. Decks are
plain JSON files, so making your own study decks takes a minute.

## Features

- Decks stored as simple JSON files in the `decks/` folder (two example decks included)
- Shuffled cards every round: see the front, press Enter to reveal the back
- Mark each card right or wrong yourself
- Score summary at the end of every round
- Optional retry rounds with only the cards you missed
- Interactive deck picker, or jump straight into a deck from the command line

## Requirements

- Python 3.6+
- No external packages - standard library only

## Installation

```bash
git clone https://github.com/Zezo998/flashcard-quizzer.git
cd flashcard-quizzer
```

## Usage

List the available decks:

```bash
python flashcard_quizzer.py decks
```

Pick a deck from the interactive menu:

```bash
python flashcard_quizzer.py
```

Jump straight into a deck by name:

```bash
python flashcard_quizzer.py quiz python_basics
```

A round looks like this:

```
=== World Capitals (6 cards) ===
Press Enter to reveal the answer, then mark yourself y (right) or n (wrong).

Card 1/6
  Q: What is the capital of Brazil?
  ... press Enter to reveal ...
  A: Brasilia
  Did you get it right? (y/n) y

--- Round over ---
  Right: 4/6 (67%)
  Wrong: 2/6

Retry the 2 card(s) you missed? (y/n) y
```

## How it works

- **Decks are JSON files.** Each file in `decks/` has a `name` and a list of
  `cards`, and each card has a `front` and a `back`:

  ```json
  {
    "name": "My Deck",
    "cards": [
      {"front": "The question", "back": "The answer"}
    ]
  }
  ```

  To make your own deck, copy one of the examples, change the cards, and save
  it as a new `.json` file in `decks/`. It shows up in the menu automatically.

- **Quiz logic.** The app reads the deck with `json.load()`, shuffles a copy
  of the card list with `random.shuffle()`, and walks through it one card at
  a time. Cards you mark wrong are collected in a list; if you choose to
  retry, that list becomes the deck for the next round.

## Project structure

```
flashcard-quizzer/
├── flashcard_quizzer.py   # the whole app
├── decks/
│   ├── python_basics.json # example deck: beginner Python questions
│   └── world_capitals.json# example deck: geography
└── README.md
```
