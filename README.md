# Soup Queue Chaos Simulator

> *"No soup for you!"*
> A comedic simulation game inspired by the Soup Nazi episode of Seinfeld.

---

## What Is This

You manage the queue at New York's most feared soup shop. The Soup Nazi
judges every customer on HOW they order - their approach, their tone,
their size, and their side. Get all four right and they get soup.
Get any wrong and they get a warning. Three warnings means banned forever.

The twist: **the soup itself is your free choice**. Jerry can order tomato
or bisque or french onion. The Soup Nazi does not care what soup you pick.
He cares how you pick it.

---

## Files

| File | Purpose |
|---|---|
| `main.py` | Entry point - run this |
| `characters.py` | Character data and win conditions |
| `engine.py` | Game logic and order evaluation |
| `dialogue.py` | All dialogue strings and autoplay scripts |
| `music.py` | Procedural Seinfeld-style bass music |
| `requirements.txt` | Dependencies |
| `README.md` | This file |
| `cheatsheet.txt` | Complete win conditions for every character |
| `gameplay.txt` | Full gameplay guide screen by screen |
| `explanation.txt` | Code explanation for every file |
| `demo.txt` | Step by step presentation demonstration |

---

## Installation

### Requirements
- Python 3.11 or higher
- Windows PowerShell (or any terminal)

### Steps

```powershell
# 1. Unzip the folder and navigate to it
cd C:\Users\YourName\Desktop\soup_queue_chaos

# 2. Create a virtual environment
python -m venv venv

# 3. Activate it
venv\Scripts\Activate.ps1

# If you get a permissions error run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 4. Install pygame
pip install -r requirements.txt

# 5. Run the game
python main.py
```

---

## How to Play

### The Order Format
```
size  soup  side
```
Examples:
```
medium tomato bread
large french onion crackers
small bisque nothing
```
No comma needed. Uppercase works. Any valid soup works.

### What You Must Get Right Per Character

| Character | Action | Dialogue | Size | Side |
|---|---|---|---|---|
| Jerry | 2 | 4 | medium | bread |
| Elaine | 5 | 5 | large | crackers |
| George | 3 | 4 | small | crackers |
| Kramer | 4 | 4 | large | bread |
| Newman | 5 | 1 | large | bread |

### Screen Flow
```
Title → Character Select → Prep (15s study) →
Action Select → Dialogue Select → Order Type (25s) →
Result → repeat
```

---

## Autoplay Modes

**Chaos Mode** - All five characters storm the counter at once.
Nobody follows the rules. Everyone gets banned. 19 lines of comedy.
Press ENTER to advance each line.

**Revenge Mode** - Elaine returns with the Soup Nazi's complete recipe book.
A 12-line scripted confrontation. Press ENTER to advance each line.

---

## Controls

| Key / Click | Screen | Action |
|---|---|---|
| Click button | Title | Choose mode |
| Click card | Character select | Choose character |
| ENTER | Prep screen | Skip to counter |
| Click button 1-5 | Action / Dialogue | Make selection |
| Type + ENTER | Order screen | Submit order |
| Click CONTINUE | Result screen | Next character |
| ENTER or Click NEXT | Autoplay | Advance one line |
| S | Autoplay | Cycle speed |
| Click SKIP ALL | Autoplay | Jump to end |

---

## Scoring

| Event | Points |
|---|---|
| Soup granted | +100 base |
| Speed bonus | +2 per second under 25s |
| Any warning | -10 to -20 |
| Getting banned | -20 extra |
| Perfect game | ~700 pts |

---

## Tips

- Soup is free. Do not worry about it. Focus on size and side.
- Newman is the exception - he wins by being MORE dramatic (dialogue 1).
- Use the 15-second prep screen to confirm the character's size and side.
- The live reading on the order screen shows what the game understood.
  Watch for size and side to highlight green before pressing ENTER.
- Read the result screen after a warning - it tells you exactly what was wrong.
