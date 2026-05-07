"""
characters.py

NEW RULES:
  - Player can order ANY soup they like. Soup is a free choice.
  - What is character-specific:
      action    — how they approach (must match)
      dialogue  — their tone (must match)
      size      — each character has a preferred size (must match)
      side      — each character's personality-specific extra (must match)
  - Soup does NOT affect whether you get soup or not.
    The Soup Nazi judges HOW you order, not WHAT soup you pick.

Character sides (personality-driven):
  Jerry   → bread      (safe, sensible, no fuss)
  Elaine  → crackers   (independent, refuses to conform to bread)
  George  → crackers   (copies Elaine, can't decide for himself)
  Kramer  → bread      (goes big, classic, no thought required)
  Newman  → bread      (extra bread, always, it's non-negotiable)
"""

from dataclasses import dataclass

SOUPS = [
    "tomato",
    "bisque",
    "chicken noodle",
    "minestrone",
    "clam chowder",
    "french onion",
    "lentil",
    "gazpacho",
]

SIDES = ["bread", "crackers", "croutons", "butter", "nothing"]
SIZES = ["small", "medium", "large"]


@dataclass
class Rules:
    """What the Soup Nazi actually checks. Soup is NOT here."""
    action:   int    # 0-based index into actions list
    dialogue: int    # 0-based index into dialogues list
    size:     str    # character's required size
    side:     str    # character's personality-specific side
    seconds:  float  # time limit for typing order


@dataclass
class Character:
    name:      str
    color:     tuple
    bio:       str
    side_note: str    # explains WHY this character takes this side
    size_note: str    # explains WHY this character orders this size
    actions:   list
    dialogues: list
    rules:     Rules
    warnings:  int  = 0
    banned:    bool = False
    got_soup:  bool = False

    def add_warning(self) -> bool:
        self.warnings += 1
        if self.warnings >= 3:
            self.banned = True
        return self.banned


def make_characters() -> list:
    return [
        Character(
            name      = "Jerry",
            color     = (100, 180, 255),
            bio       = "Polite. Compliant. Just wants to get through this.",
            side_note = "Jerry always takes bread. Safe. Predictable. That is Jerry.",
            size_note = "Medium. Never too much, never too little.",
            actions   = [
                "Step forward politely",
                "Shuffle with full compliance",
                "Nod and make eye contact",
                "Stand at exact correct distance",
                "Clear throat quietly",
            ],
            dialogues = [
                "Casual and friendly",
                "Overly formal",
                "Bemused and self-aware",
                "Rapid and efficient",
                "Quiet mumble",
            ],
            rules = Rules(
                action=1, dialogue=3,
                size="medium", side="bread",
                seconds=25,
            ),
        ),

        Character(
            name      = "Elaine",
            color     = (255, 130, 180),
            bio       = "Confident. Defiant. Has been banned twice already.",
            side_note = "Elaine takes crackers. She refuses to take bread just because everyone else does.",
            size_note = "Large. She is not here to be modest.",
            actions   = [
                "Approach with confidence",
                "Mimic the shuffle sarcastically",
                "Fake a sneeze to stall",
                "Nudge person in front",
                "Walk straight to counter",
            ],
            dialogues = [
                "Loud and rude",
                "Sweetly sarcastic",
                "Oblivious to all rules",
                "Apologetically nervous",
                "Brisk and businesslike",
            ],
            rules = Rules(
                action=4, dialogue=4,
                size="large", side="crackers",
                seconds=25,
            ),
        ),

        Character(
            name      = "George",
            color     = (255, 210, 80),
            bio       = "Paranoid. Over-rehearsed. Freezes under pressure.",
            side_note = "George takes crackers. He saw Elaine do it once and has copied her ever since.",
            size_note = "Small. He is cheap and slightly ashamed of how much he wants this.",
            actions   = [
                "Inch forward pretending not to",
                "Ask a clarifying question first",
                "Rehearse order under his breath",
                "Freeze and stare blankly",
                "Trip approaching the counter",
            ],
            dialogues = [
                "Paranoid and defensive",
                "Incoherently rambling",
                "Lying about qualifications",
                "Whispering the order",
                "Accidentally shouting",
            ],
            rules = Rules(
                action=2, dialogue=3,
                size="small", side="crackers",
                seconds=25,
            ),
        ),

        Character(
            name      = "Kramer",
            color     = (80, 220, 120),
            bio       = "Chaotic. Enthusiastic. Somehow always ends up behind the counter.",
            side_note = "Kramer takes bread. He did not think about it. He just said bread.",
            size_note = "Large. Of course large. Did you even have to ask?",
            actions   = [
                "Burst through the door dramatically",
                "Slide up sideways",
                "Lean on Newman for support",
                "Enter backwards somehow",
                "Stand exactly where he should not",
            ],
            dialogues = [
                "Rapid stream of consciousness",
                "Confident but entirely wrong",
                "Referencing an unrelated scheme",
                "Surprisingly soft and sincere",
                "Pure sound effects and gestures",
            ],
            rules = Rules(
                action=3, dialogue=3,
                size="large", side="bread",
                seconds=25,
            ),
        ),

        Character(
            name      = "Newman",
            color     = (190, 100, 220),
            bio       = "Operatic. Obsessive. Has been rehearsing since 6am.",
            side_note = "Newman always takes bread. Extra bread if possible. He has asked about extra bread before. The answer was no.",
            size_note = "Large. Newman does not do small. Newman does not do medium.",
            actions   = [
                "Waddle forward with great purpose",
                "Edge sideways like a chess piece",
                "Bow slightly before approaching",
                "Signal with a knowing wink",
                "Announce himself formally",
            ],
            dialogues = [
                "Dramatic and operatic",
                "Whimpering with anticipation",
                "Barely contained excitement",
                "Pretending this is completely normal",
                "Reciting a prepared speech",
            ],
            rules = Rules(
                action=4, dialogue=0,
                size="large", side="bread",
                seconds=25,
            ),
        ),
    ]
