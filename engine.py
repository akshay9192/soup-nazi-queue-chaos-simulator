"""
engine.py — Game logic engine.

NEW EVALUATION RULES:
  - ANY soup is valid. The player picks whatever they want.
  - The Soup Nazi judges:
      1. action    — correct approach for this character
      2. dialogue  — correct tone for this character
      3. size      — character's required size
      4. side      — character's personality-specific side
  - Soup never causes a warning. It is acknowledged but not judged.
  - Timeout still causes a warning.
  - Unreadable order still causes a warning.

This means:
  Jerry can order tomato, bisque, french onion — anything.
  He just must approach correctly, speak efficiently,
  order medium, and take bread.
"""

from characters import Character, SOUPS, SIDES, SIZES


def parse_order(raw: str) -> dict | None:
    """
    Parse free-text order into {size, soup, side}.
    Soup can be anything in SOUPS.
    Returns None only if size or side are missing/unrecognised,
    or if no soup words remain in the middle.
    """
    text  = raw.strip().lower().replace(",", "").replace(".", "")
    words = text.split()

    if not words:
        return None

    # ── Size (first word) ────────────────────────────────────────────────────
    size = None
    for s in SIZES:
        if words[0] == s:
            size = s
            words = words[1:]
            break
    if size is None:
        return None

    # ── Side (from the end, longest first) ───────────────────────────────────
    side = None
    for sd in sorted(SIDES, key=len, reverse=True):
        sd_words = sd.split()
        if words[-len(sd_words):] == sd_words:
            side = sd
            words = words[:-len(sd_words)]
            break
    if side is None:
        return None

    # ── Soup (everything in between) ─────────────────────────────────────────
    soup_guess = " ".join(words)
    if not soup_guess:
        return None

    # Exact match
    if soup_guess in SOUPS:
        return {"size": size, "soup": soup_guess, "side": side}

    # Fuzzy match — find the soup that contains all typed words
    for soup in sorted(SOUPS, key=len, reverse=True):
        if all(w in soup for w in words):
            return {"size": size, "soup": soup, "side": side}

    # Soup not recognised — still return with soup marked unknown
    # so we can give a specific error message about it
    return {"size": size, "soup": soup_guess, "side": side, "unknown_soup": True}


class Engine:
    """Evaluates each turn. Mood is the only persistent state."""

    def __init__(self):
        self.mood = 60

    def mood_label(self) -> str:
        if self.mood <= 20: return "FURIOUS"
        if self.mood <= 45: return "Annoyed"
        if self.mood <= 65: return "Neutral"
        if self.mood <= 85: return "Pleased"
        return "Ecstatic"

    def mood_color(self) -> tuple:
        if self.mood <= 20: return (220,  40,  40)
        if self.mood <= 45: return (220, 130,  30)
        if self.mood <= 65: return (200, 200,  30)
        if self.mood <= 85: return ( 80, 200,  80)
        return (80, 200, 200)

    def _shift(self, delta: int):
        self.mood = max(0, min(100, self.mood + delta))

    def evaluate(self, char: Character, raw: str,
                 action: int, dialogue: int, elapsed: float) -> dict:
        """
        Returns dict with keys:
          outcome  : "soup" | "warning" | "ban"
          message  : str   — what the Soup Nazi says out loud
          points   : int
          detail   : str   — explanation shown to player
          soup_note: str   — friendly acknowledgement of their soup choice
        """
        parsed = parse_order(raw)
        r      = char.rules

        # ── Cannot parse at all ───────────────────────────────────────────────
        if parsed is None:
            self._shift(-8)
            return self._warn(
                char,
                "SOUP NAZI: 'What IS that?! I cannot understand a word!'",
                "Could not read your order.\n"
                "Format:  size  soup  side\n"
                "Example: medium tomato bread",
                -15,
                soup_note="",
            )

        size = parsed["size"]
        soup = parsed["soup"]
        side = parsed["side"]
        unknown_soup = parsed.get("unknown_soup", False)

        # ── Unknown soup — warn specifically about this ───────────────────────
        if unknown_soup:
            self._shift(-6)
            return self._warn(
                char,
                f"SOUP NAZI: '{soup}?! That is not on my menu!'",
                f"'{soup}' is not a valid soup. Check the menu on the right.",
                -10,
                soup_note="",
            )

        # Soup acknowledgement line (shown on result screen, not a warning)
        soup_note = f"{char.name} ordered the {soup}."

        # ── Timed out ─────────────────────────────────────────────────────────
        if elapsed >= r.seconds:
            self._shift(-10)
            return self._warn(
                char,
                "SOUP NAZI: 'TOO SLOW! NEXT!'",
                f"You took {elapsed:.0f}s. You have {r.seconds:.0f}s.",
                -20,
                soup_note=soup_note,
            )

        # ── Wrong action ──────────────────────────────────────────────────────
        if action != r.action:
            self._shift(-6)
            correct = char.actions[r.action]
            return self._warn(
                char,
                "SOUP NAZI: 'Your APPROACH was all wrong! STAND BACK!'",
                f"Wrong approach for {char.name}.\nCorrect approach:  {correct}",
                -10,
                soup_note=soup_note,
            )

        # ── Wrong dialogue ────────────────────────────────────────────────────
        if dialogue != r.dialogue:
            self._shift(-6)
            correct = char.dialogues[r.dialogue]
            return self._warn(
                char,
                "SOUP NAZI: 'That TONE is completely unacceptable!'",
                f"Wrong tone for {char.name}.\nCorrect tone:  {correct}",
                -10,
                soup_note=soup_note,
            )

        # ── Wrong size ────────────────────────────────────────────────────────
        if size != r.size:
            self._shift(-6)
            return self._warn(
                char,
                f"SOUP NAZI: '{size}?! {char.name} always orders {r.size}!'",
                f"{char.name} orders {r.size}.\n{char.size_note}",
                -10,
                soup_note=soup_note,
            )

        # ── Wrong side ────────────────────────────────────────────────────────
        if side != r.side:
            self._shift(-6)
            return self._warn(
                char,
                f"SOUP NAZI: '{side}?! {char.name} always takes {r.side}!'",
                f"{char.name} always takes {r.side}.\n{char.side_note}",
                -10,
                soup_note=soup_note,
            )

        # ── PERFECT — soup, action, dialogue, size, side all correct ─────────
        self._shift(+10)
        speed_bonus = max(0, int((r.seconds - elapsed) * 2))
        points      = 100 + speed_bonus

        from dialogue import nazi_ok
        return {
            "outcome":   "soup",
            "message":   f"SOUP NAZI: '{nazi_ok()}'",
            "points":    points,
            "detail":    f"Perfect order! +{points} pts  (speed bonus +{speed_bonus})",
            "soup_note": soup_note,
        }

    def _warn(self, char: Character, message: str,
              detail: str, points: int, soup_note: str) -> dict:
        from dialogue import nazi_ban
        banned  = char.add_warning()
        outcome = "ban" if banned else "warning"
        if banned:
            message = f"SOUP NAZI: '{nazi_ban()}'"
            points -= 20
        self._shift(-3)
        return {
            "outcome":   outcome,
            "message":   message,
            "points":    points,
            "detail":    detail,
            "soup_note": soup_note,
        }
