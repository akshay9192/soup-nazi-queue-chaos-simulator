"""dialogue.py — All Soup Nazi and character lines."""
import random

NAZI_OK = [
    "...Fine. Here is your soup. Do NOT thank me.",
    "Acceptable. Take it. Go.",
    "Correct. You may have soup.",
    "This time. Only this time.",
]

NAZI_WARN = [
    "NO! You move FORWARD, then you ORDER!",
    "What is THIS?! That is not how you order!",
    "STAND BACK! You are doing it ALL wrong!",
    "I have STANDARDS. Learn them.",
    "You think soup is a GAME?! It is NOT.",
    "That tone is UNACCEPTABLE.",
    "Your approach was WRONG. Step back.",
    "I am watching. I am ALWAYS watching.",
]

NAZI_BAN = [
    "NO SOUP FOR YOU! Come back NEVER.",
    "OUT! OUT! OUT! You are BANNED!",
    "You have INSULTED the soup. GET OUT.",
    "SECURITY! Remove this person! NO SOUP. ONE YEAR!",
    "BANNED. GOODBYE. FOREVER.",
]

CHAR_QUIPS = {
    "Jerry":  [
        "Jerry mutters: 'What is the deal with soup rules?'",
        "Jerry: 'I stood in line 40 minutes to be terrified. Worth it.'",
        "Jerry: 'He has ONE product and I'm somehow not qualified to buy it.'",
    ],
    "Elaine": [
        "Elaine: 'I am NOT doing the shuffle. I have DIGNITY.'",
        "Elaine: 'He banned me TWICE. I consider it a badge of honour.'",
        "Elaine: 'You know what? I WILL make a scene. Watch me.'",
    ],
    "George": [
        "George: 'I rehearsed this order in the mirror fourteen times.'",
        "George: 'I don't NEED soup. I WANT soup. There's a difference.'",
        "George whispers: 'What if I stood on one leg?'",
    ],
    "Kramer": [
        "Kramer bursts in: 'What is THIS?! You call this a LINE?!'",
        "Kramer: 'Heyyy, the Soup Nazi! What's cookin'?'",
        "Kramer slides up: 'I'll take the lobster bisque!'",
    ],
    "Newman": [
        "Newman trembles: 'The soup... the BEAUTIFUL soup... it calls to me.'",
        "Newman: 'I have been strategising this order since 7am, Jerry.'",
        "Newman: 'One does not simply approach the Soup Nazi unprepared.'",
    ],
}

REVENGE_LINES = [
    "ELAINE walks in holding a large armoire.",
    "ELAINE: 'Hello. I have your RECIPES.'",
    "SOUP NAZI: '...You wouldn't.'",
    "ELAINE: 'Every. Single. One. Right here.'",
    "SOUP NAZI: '...What do you want.'",
    "ELAINE: 'No soup for YOU!'",
    "SOUP NAZI stares into the middle distance.",
    "SOUP NAZI quietly packs up his ladle.",
    "SOUP NAZI: 'I am moving to Argentina.'",
    "ELAINE: 'Bon voyage!'",
    "[ A single tear falls. The bisque goes cold. ]",
    "[ REVENGE COMPLETE ]",
]

CHAOS_LINES = [
    "[ ALL FIVE enter at once. Nobody shuffles. ]",
    "JERRY: 'What is the DEAL with having a line?'",
    "GEORGE: 'I was here first! I was DEFINITELY here first!'",
    "KRAMER slides behind the counter somehow.",
    "NEWMAN: 'THE BISQUE. I CAN SMELL THE BISQUE FROM HERE.'",
    "ELAINE: 'I am not shuffling. That's final.'",
    "SOUP NAZI: '...One at a time. ONE. AT. A. TIME.'",
    "GEORGE: 'Can I ask a question about the lentil?'",
    "SOUP NAZI: 'NO.'",
    "KRAMER: 'Hey, where do you keep the ladles?'",
    "SOUP NAZI: 'Get OUT from behind my counter!'",
    "NEWMAN eating directly from the pot.",
    "JERRY: 'Newman!'",
    "NEWMAN: 'What? It is INCREDIBLE.'",
    "ELAINE snaps a photo of the recipe board.",
    "SOUP NAZI: 'NO SOUP FOR ANY OF YOU. EVER.'",
    "[ He closes the shop. Moves to Argentina. ]",
    "[ Somehow there is already a line there. ]",
    "[ CHAOS COMPLETE ]",
]


def nazi_warn():  return random.choice(NAZI_WARN)
def nazi_ban():   return random.choice(NAZI_BAN)
def nazi_ok():    return random.choice(NAZI_OK)
def char_quip(name): return random.choice(CHAR_QUIPS.get(name, CHAR_QUIPS["Jerry"]))
