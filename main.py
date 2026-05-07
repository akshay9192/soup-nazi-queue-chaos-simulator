"""
main.py — Soup Queue Chaos Simulator  (complete rewrite v3)

SCREEN FLOW
───────────
TITLE → CHARACTER_SELECT → PREP (15s study) → ACTION_SELECT →
DIALOGUE_SELECT → ORDER_TYPE (25s) → RESULT → (next char or END)

CHAOS_MODE and REVENGE_MODE are separate flows from the title.

DESIGN PRINCIPLES (v3)
- One thing on screen at a time. No cluttered panels.
- Click big buttons. No memorising keys.
- Order format: SIZE SOUP SIDE  (no comma, no special punctuation)
- All text is large and readable.
- Dialogue log is the CENTRE of the screen, not an afterthought.
- The right side panel only shows the active menu when needed.
"""

import pygame
import sys
import time
import random
from enum import Enum, auto

import music
from characters import make_characters, SOUPS, SIZES, SIDES
from engine import Engine, parse_order
from dialogue import (char_quip, nazi_warn, nazi_ok, nazi_ban,
                      REVENGE_LINES, CHAOS_LINES)

# ── Palette ───────────────────────────────────────────────────────────────────
BG        = ( 14,   8,   4)
PANEL     = ( 28,  16,   8)
GOLD      = (212, 170,  50)
WHITE     = (255, 255, 255)
CREAM     = (255, 245, 210)
GREY      = (140, 140, 140)
DGREY     = ( 50,  50,  50)
RED       = (210,  40,  40)
DRED      = (140,  10,  10)
GREEN     = ( 60, 190,  60)
YELLOW    = (230, 195,  30)
ORANGE    = (220, 120,  20)
LREY      = (190, 190, 190)

# ── Layout ────────────────────────────────────────────────────────────────────
W, H = 1100, 720
FPS  = 60

# Left column  — queue / character info
LC_X, LC_W = 10, 230
# Centre       — main focus area
CC_X, CC_W = 250, 600
# Right column — contextual menu / hint
RC_X, RC_W = 860, 230


def run():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Soup Queue Chaos Simulator")
    clock  = pygame.time.Clock()
    music.start(pygame)

    # ── Font cache ────────────────────────────────────────────────────────────
    F = {
        "h1":    pygame.font.SysFont("couriernew", 42, bold=True),
        "h2":    pygame.font.SysFont("couriernew", 28, bold=True),
        "h3":    pygame.font.SysFont("couriernew", 20, bold=True),
        "body":  pygame.font.SysFont("couriernew", 17),
        "small": pygame.font.SysFont("couriernew", 14),
    }

    # ── Helper renderers ──────────────────────────────────────────────────────
    def txt(surface, fkey, text, x, y, color=WHITE, max_w=None):
        """Blit text, return bottom y."""
        if max_w:
            words = text.split()
            line, lines = "", []
            for w in words:
                test = (line + " " + w).strip()
                if F[fkey].size(test)[0] <= max_w:
                    line = test
                else:
                    if line: lines.append(line)
                    line = w
            if line: lines.append(line)
        else:
            lines = [text]
        for ln in lines:
            surf = F[fkey].render(ln, True, color)
            surface.blit(surf, (x, y))
            y += surf.get_height() + 2
        return y

    def box(surface, rect, bg=PANEL, border=GOLD, radius=8):
        pygame.draw.rect(surface, bg, rect, border_radius=radius)
        pygame.draw.rect(surface, border, rect, 2, border_radius=radius)

    def btn(surface, rect, label, fkey="h3",
            bg=DGREY, fg=WHITE, border=GOLD, hover=False):
        """Draw a button, return rect."""
        b = bg if not hover else tuple(min(255, c+40) for c in bg)
        pygame.draw.rect(surface, b, rect, border_radius=6)
        pygame.draw.rect(surface, border, rect, 2, border_radius=6)
        surf = F[fkey].render(label, True, fg)
        cx   = rect.x + rect.w // 2 - surf.get_width() // 2
        cy   = rect.y + rect.h // 2 - surf.get_height() // 2
        surface.blit(surf, (cx, cy))
        return rect

    def hovered(rect):
        mx, my = pygame.mouse.get_pos()
        return rect.collidepoint(mx, my)

    def clicked(events, rect):
        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if rect.collidepoint(ev.pos):
                    return True
        return False

    def draw_mood(surface, engine, y_top):
        """Thin mood bar across the top of the centre column."""
        bx, by = CC_X, y_top
        bw, bh = CC_W, 18
        pygame.draw.rect(surface, DGREY, (bx, by, bw, bh))
        fill = int(bw * engine.mood / 100)
        pygame.draw.rect(surface, engine.mood_color(), (bx, by, fill, bh))
        pygame.draw.rect(surface, GOLD, (bx, by, bw, bh), 1)
        label = f"Soup Nazi: {engine.mood_label()}  ({engine.mood}/100)"
        lsurf = F["small"].render(label, True, engine.mood_color())
        surface.blit(lsurf, (bx + 4, by + 2))

    def draw_queue_panel(surface, chars_left, all_chars, score):
        """Left column: queue + score."""
        box(surface, pygame.Rect(LC_X, 10, LC_W, H - 20))
        y = txt(surface, "small", "[ QUEUE ]", LC_X + 10, 20, GOLD)
        y += 6
        for ch in all_chars:
            if ch in chars_left:
                arrow = "> " if ch == chars_left[0] else "  "
                col   = ch.color if ch == chars_left[0] else GREY
                y = txt(surface, "body", f"{arrow}{ch.name}", LC_X + 10, y, col)
                # warning pips
                for w in range(ch.warnings):
                    pygame.draw.circle(surface, RED, (LC_X + 175 + w*12, y - 10), 5)
            else:
                # served or banned
                col = GREEN if ch.got_soup else DRED
                label = f"  {ch.name}  {'✓' if ch.got_soup else 'X'}"
                y = txt(surface, "body", label, LC_X + 10, y, col)
            y += 4

        # Score at bottom of queue panel
        sy = H - 80
        pygame.draw.line(surface, GOLD, (LC_X + 10, sy), (LC_X + LC_W - 10, sy), 1)
        txt(surface, "small", "SCORE", LC_X + 10, sy + 8, GREY)
        txt(surface, "h2", str(score), LC_X + 10, sy + 24, GOLD)

    def draw_log(surface, log: list[str], y_start: int, max_lines=10):
        """
        Dialogue log — centre column, bottom section.
        Most recent lines at the bottom.
        """
        log_rect = pygame.Rect(CC_X, y_start, CC_W, H - y_start - 10)
        box(surface, log_rect, bg=(10, 6, 2))
        txt(surface, "small", "[ WHAT HAPPENED ]", CC_X + 10, y_start + 6, GOLD)

        visible = log[-max_lines:]
        y = log_rect.bottom - 14
        for line in reversed(visible):
            col = (YELLOW  if "SOUP NAZI:" in line
                   else GREEN  if "SOUP for" in line or "Perfect" in line.upper()
                   else RED    if "BANNED" in line or "NO SOUP" in line
                   else ORANGE if "WARNING" in line
                   else LREY   if line.startswith("[") else LREY)
            words  = line.split()
            chunks = []
            cur    = ""
            for w in words:
                test = (cur + " " + w).strip()
                if F["small"].size(test)[0] <= CC_W - 20:
                    cur = test
                else:
                    if cur: chunks.append(cur)
                    cur = w
            if cur: chunks.append(cur)
            for chunk in reversed(chunks):
                surf = F["small"].render(chunk, True, col)
                y   -= surf.get_height() + 1
                surface.blit(surf, (CC_X + 10, y))
            y -= 4
            if y < y_start + 24: break

    def draw_menu_panel(surface, highlight_size=None, highlight_side=None):
        """Right column: always-visible menu reference."""
        box(surface, pygame.Rect(RC_X, 10, RC_W, H - 20))
        y = txt(surface, "small", "[ MENU ]", RC_X + 8, 20, GOLD) + 6

        txt(surface, "small", "SIZES:", RC_X + 8, y, GOLD)
        y += 16
        for s in SIZES:
            col = GREEN if s == highlight_size else CREAM
            y = txt(surface, "small", f"  {s}", RC_X + 8, y, col)

        y += 8
        txt(surface, "small", "SOUPS (your choice):", RC_X + 8, y, GOLD)
        y += 16
        for s in SOUPS:
            y = txt(surface, "small", f"  {s}", RC_X + 8, y, CREAM)

        y += 8
        txt(surface, "small", "SIDES:", RC_X + 8, y, GOLD)
        y += 16
        for s in SIDES:
            col = GREEN if s == highlight_side else CREAM
            y = txt(surface, "small", f"  {s}", RC_X + 8, y, col)

        y += 12
        txt(surface, "small", "FORMAT:", RC_X + 8, y, GOLD)
        y += 16
        txt(surface, "small", "size soup side", RC_X + 8, y, YELLOW)
        y += 16
        txt(surface, "small", "e.g.", RC_X + 8, y, GREY)
        y += 16
        txt(surface, "small", "medium tomato", RC_X + 8, y, CREAM)
        y += 16
        txt(surface, "small", "bread", RC_X + 8, y, CREAM)

    # ══════════════════════════════════════════════════════════════════════════
    # SCREEN FUNCTIONS
    # ══════════════════════════════════════════════════════════════════════════

    # ── TITLE ─────────────────────────────────────────────────────────────────
    def screen_title():
        while True:
            events = pygame.event.get()
            for ev in events:
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()

            screen.fill(BG)

            y = 80
            y = txt(screen, "h1", "SOUP QUEUE", CC_X, y, GOLD) + 4
            y = txt(screen, "h1", "CHAOS SIMULATOR", CC_X, y, GOLD) + 20
            y = txt(screen, "body", "Inspired by the Soup Nazi — Seinfeld", CC_X, y, CREAM) + 40

            r_play   = pygame.Rect(CC_X + 80, y,      440, 55)
            r_chaos  = pygame.Rect(CC_X + 80, y + 70, 440, 55)
            r_revenge= pygame.Rect(CC_X + 80, y +140, 440, 55)
            r_quit   = pygame.Rect(CC_X + 80, y +220, 440, 45)

            btn(screen, r_play,    "START GAME",          hover=hovered(r_play))
            btn(screen, r_chaos,   "CHAOS MODE (autoplay)",hover=hovered(r_chaos),   bg=(60,20,20))
            btn(screen, r_revenge, "REVENGE MODE (Elaine)",hover=hovered(r_revenge), bg=(50,10,50))
            btn(screen, r_quit,    "QUIT",                 hover=hovered(r_quit),    bg=DGREY, fg=GREY)

            y2 = y + 290
            txt(screen, "small", "FORMAT:  size  soup  side   (no comma needed)", CC_X + 40, y2, GREY)
            txt(screen, "small", "e.g.     medium  tomato  bread", CC_X + 40, y2 + 18, GREY)
            txt(screen, "small", "3 warnings per character = BANNED", CC_X + 40, y2 + 36, RED)

            pygame.display.flip()
            clock.tick(FPS)

            if clicked(events, r_play):    return "play"
            if clicked(events, r_chaos):   return "chaos"
            if clicked(events, r_revenge): return "revenge"
            if clicked(events, r_quit):    pygame.quit(); sys.exit()

    # ── CHARACTER SELECT ──────────────────────────────────────────────────────
    def screen_char_select(all_chars):
        """Click-based character picker. Returns chosen Character."""
        while True:
            events = pygame.event.get()
            for ev in events:
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()

            screen.fill(BG)
            txt(screen, "h2", "WHO DO YOU WANT TO PLAY AS?", CC_X + 20, 30, GOLD)
            txt(screen, "body", "Click a character to begin their turn.", CC_X + 20, 72, GREY)

            btns = []
            for i, ch in enumerate(all_chars):
                r = pygame.Rect(CC_X + 20, 120 + i * 100, CC_W - 40, 85)
                bg = (30, 20, 10) if not hovered(r) else (50, 35, 15)
                box(screen, r, bg=bg, border=ch.color)
                txt(screen, "h3", ch.name, r.x + 16, r.y + 10, ch.color)
                txt(screen, "small", ch.bio, r.x + 16, r.y + 40, LREY, max_w=CC_W - 60)
                btns.append((r, ch))

            pygame.display.flip()
            clock.tick(FPS)

            for r, ch in btns:
                if clicked(events, r):
                    return ch

    # ── PREP ──────────────────────────────────────────────────────────────────
    def screen_prep(char, all_chars, score, engine, log):
        """
        15 seconds to study the menu only.
        No typing here. Player just reads the menu and decides.
        Press ENTER or wait for the timer to proceed.
        """
        start_t = time.time()
        limit   = 15.0

        while True:
            elapsed = time.time() - start_t
            left    = max(0.0, limit - elapsed)
            events  = pygame.event.get()

            for ev in events:
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_RETURN:
                        return   # player is ready, move on

            if left <= 0:
                return   # timer expired, move on automatically

            screen.fill(BG)
            draw_queue_panel(screen, [c for c in all_chars if not c.got_soup and not c.banned],
                             all_chars, score)
            draw_mood(screen, engine, 10)
            draw_menu_panel(screen)

            # Countdown clock
            cy = 35
            clk_col  = GREEN if left > 8 else YELLOW if left > 4 else RED
            clk_surf = F["h1"].render(f"{left:.0f}s", True, clk_col)
            screen.blit(clk_surf, (CC_X + CC_W - clk_surf.get_width() - 10, cy))

            # Next up label
            cy = txt(screen, "h2", f"NEXT UP:  {char.name}", CC_X + 10, cy, char.color) + 12

            # Soup Nazi instruction box
            box(screen, pygame.Rect(CC_X + 8, cy, CC_W - 16, 72), bg=(40, 5, 5), border=RED)
            txt(screen, "h3", "SOUP NAZI:", CC_X + 16, cy + 8, RED)
            txt(screen, "body", "'STUDY THE MENU. DECIDE NOW.", CC_X + 16, cy + 32, YELLOW)
            txt(screen, "body", "DO NOT WASTE MY TIME AT THE COUNTER!'", CC_X + 16, cy + 52, YELLOW)
            cy += 84

            # Character quip
            txt(screen, "small", char_quip(char.name), CC_X + 10, cy, GREY, max_w=CC_W - 20)
            cy += 40

            # Instruction
            box(screen, pygame.Rect(CC_X + 8, cy, CC_W - 16, 44), bg=(10, 20, 10), border=GREEN)
            txt(screen, "body", "Study the menu on the right.", CC_X + 16, cy + 6, GREEN)
            txt(screen, "small", "Press ENTER when ready  (or wait for timer)", CC_X + 16, cy + 28, GREY)
            cy += 56

            # Reminder of order format + new rules
            txt(screen, "small", "ORDER FORMAT:", CC_X + 10, cy, GOLD)
            cy += 18
            txt(screen, "h3",   "size  soup  side", CC_X + 10, cy, WHITE)
            cy += 28
            txt(screen, "small", "e.g.  medium tomato bread", CC_X + 10, cy, GREY)
            cy += 18
            txt(screen, "small", "e.g.  large french onion crackers", CC_X + 10, cy, GREY)
            cy += 24
            txt(screen, "small", "SOUP = your free choice, any soup works!", CC_X + 10, cy, GREEN)
            cy += 18
            txt(screen, "small", "SIZE + SIDE = must match this character.", CC_X + 10, cy, YELLOW)

            draw_log(screen, log, H - 160)
            pygame.display.flip()
            clock.tick(FPS)

    # ── ACTION SELECT ─────────────────────────────────────────────────────────
    def screen_action(char, all_chars, score, engine, log):
        """Click one of 5 action buttons. Returns 0-based index."""
        while True:
            events = pygame.event.get()
            for ev in events:
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()

            screen.fill(BG)
            draw_queue_panel(screen, [c for c in all_chars if not c.got_soup and not c.banned],
                             all_chars, score)
            draw_mood(screen, engine, 10)
            draw_menu_panel(screen)

            cy = 35
            cy = txt(screen, "h2", f"{char.name}  —  HOW DO THEY APPROACH?", CC_X + 10, cy, char.color) + 6
            txt(screen, "small", "Pick the approach. Remember: any soup is fine, but size and side must match this character.", CC_X + 10, cy, GREY, max_w=CC_W - 20)
            cy += 30

            btns = []
            for i, act in enumerate(char.actions):
                r = pygame.Rect(CC_X + 10, cy, CC_W - 20, 52)
                is_h = hovered(r)
                box(screen, r, bg=(35, 25, 10) if not is_h else (55, 40, 15), border=GOLD)
                txt(screen, "h3", f"{i+1}.  {act}", r.x + 14, r.y + 14, WHITE)
                btns.append((r, i))
                cy += 60

            draw_log(screen, log, cy + 10)
            pygame.display.flip()
            clock.tick(FPS)

            for r, i in btns:
                if clicked(events, r):
                    return i

    # ── DIALOGUE SELECT ───────────────────────────────────────────────────────
    def screen_dialogue(char, all_chars, score, engine, log):
        """Click one of 5 dialogue-style buttons. Returns 0-based index."""
        while True:
            events = pygame.event.get()
            for ev in events:
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()

            screen.fill(BG)
            draw_queue_panel(screen, [c for c in all_chars if not c.got_soup and not c.banned],
                             all_chars, score)
            draw_mood(screen, engine, 10)
            draw_menu_panel(screen)

            cy = 35
            cy = txt(screen, "h2", f"{char.name}  —  HOW DO THEY SPEAK?", CC_X + 10, cy, char.color) + 6
            txt(screen, "small", "Click the tone of voice.", CC_X + 10, cy, GREY)
            cy += 30

            btns = []
            for i, d in enumerate(char.dialogues):
                r = pygame.Rect(CC_X + 10, cy, CC_W - 20, 52)
                is_h = hovered(r)
                box(screen, r, bg=(25, 10, 35) if not is_h else (45, 20, 60), border=GOLD)
                txt(screen, "h3", f"{i+1}.  {d}", r.x + 14, r.y + 14, WHITE)
                btns.append((r, i))
                cy += 60

            draw_log(screen, log, cy + 10)
            pygame.display.flip()
            clock.tick(FPS)

            for r, i in btns:
                if clicked(events, r):
                    return i

    # ── ORDER TYPE ────────────────────────────────────────────────────────────
    def screen_order(char, all_chars, score, engine, log):
        """
        25 seconds to type and submit an order.
        Menu visible on right. Format shown large in centre.
        Returns (raw_order_str, elapsed_seconds).
        """
        order_text = ""
        start_t    = time.time()
        limit      = 25.0
        parsed_preview = None

        while True:
            elapsed = time.time() - start_t
            left    = max(0.0, limit - elapsed)
            events  = pygame.event.get()

            for ev in events:
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_RETURN:
                        return order_text.strip(), elapsed
                    elif ev.key == pygame.K_BACKSPACE:
                        order_text = order_text[:-1]
                if ev.type == pygame.TEXTINPUT:
                    if len(order_text) < 60:
                        order_text += ev.text

            if left <= 0:
                return order_text.strip(), limit

            parsed_preview = parse_order(order_text)

            screen.fill(BG)
            draw_queue_panel(screen, [c for c in all_chars if not c.got_soup and not c.banned],
                             all_chars, score)
            draw_mood(screen, engine, 10)

            # Right panel: menu with live highlights
            hs = parsed_preview["size"] if parsed_preview else None
            hd = parsed_preview["side"] if parsed_preview else None
            draw_menu_panel(screen, highlight_size=hs, highlight_side=hd)

            cy = 35
            cy = txt(screen, "h2", f"{char.name}  —  TYPE YOUR ORDER", CC_X + 10, cy, char.color) + 8

            # Timer
            clk_col = GREEN if left > 12 else YELLOW if left > 6 else RED
            clk_surf = F["h2"].render(f"{left:.0f}s left", True, clk_col)
            screen.blit(clk_surf, (CC_X + CC_W - clk_surf.get_width() - 10, 35))

            # Format reminder
            box(screen, pygame.Rect(CC_X + 8, cy, CC_W - 16, 52), bg=(10, 25, 10), border=GREEN)
            txt(screen, "h3",   "FORMAT:   size  soup  side",     CC_X + 16, cy + 6,  GOLD)
            txt(screen, "small","EXAMPLE:  medium  tomato  bread", CC_X + 16, cy + 32, GREY)
            cy += 62

            # Input box
            txt(screen, "small", "Your order:", CC_X + 10, cy, YELLOW)
            cy += 20
            input_r = pygame.Rect(CC_X + 10, cy, CC_W - 20, 46)
            pygame.draw.rect(screen, (8, 28, 8), input_r, border_radius=6)
            border_col = GREEN if parsed_preview else GOLD
            pygame.draw.rect(screen, border_col, input_r, 2, border_radius=6)
            txt(screen, "h3", order_text + "|", CC_X + 18, cy + 10, WHITE)
            cy += 56

            # Live parse feedback
            if order_text.strip():
                if parsed_preview:
                    txt(screen, "body",
                        f"Reading:  {parsed_preview['size']}  {parsed_preview['soup']}  {parsed_preview['side']}",
                        CC_X + 10, cy, GREEN)
                else:
                    txt(screen, "body", "Cannot read order yet — keep typing", CC_X + 10, cy, ORANGE)
            cy += 30

            txt(screen, "small", "Press ENTER to submit", CC_X + 10, cy, GREY)

            draw_log(screen, log, H - 200)
            pygame.display.flip()
            clock.tick(FPS)

    # ── RESULT ────────────────────────────────────────────────────────────────
    def screen_result(result: dict, char, all_chars, score, engine, log):
        """
        Big clear result screen. Player clicks Continue.
        Shows exactly what the Soup Nazi said + why + points.
        """
        r_continue = pygame.Rect(CC_X + 140, H - 100, 320, 55)

        while True:
            events = pygame.event.get()
            for ev in events:
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                    return

            screen.fill(BG)
            draw_queue_panel(screen, [c for c in all_chars if not c.got_soup and not c.banned],
                             all_chars, score)
            draw_mood(screen, engine, 10)
            draw_menu_panel(screen)

            outcome = result["outcome"]
            oc_col  = GREEN if outcome == "soup" else RED if outcome == "ban" else ORANGE

            cy = 40
            # Big outcome label
            label = ("SOUP!" if outcome == "soup"
                     else "BANNED!" if outcome == "ban"
                     else f"WARNING  #{char.warnings}/3")
            cy = txt(screen, "h1", label, CC_X + 20, cy, oc_col) + 10

            # What the Soup Nazi said — large box
            box(screen, pygame.Rect(CC_X + 8, cy, CC_W - 16, 70),
                bg=(40, 25, 5), border=YELLOW)
            txt(screen, "body", result["message"], CC_X + 16, cy + 10, YELLOW, max_w=CC_W - 30)
            cy += 80

            # Why
            box(screen, pygame.Rect(CC_X + 8, cy, CC_W - 16, 80),
                bg=(20, 20, 20), border=GREY)
            txt(screen, "body", result["detail"], CC_X + 16, cy + 10, LREY, max_w=CC_W - 30)
            cy += 90

            # Soup note
            soup_note = result.get("soup_note", "")
            if soup_note:
                txt(screen, "small", soup_note, CC_X + 20, cy, GREY)
                cy += 24
            # Points
            pts = result["points"]
            pts_col = GREEN if pts > 0 else RED
            txt(screen, "h3", f"Points this turn:  {'+' if pts>0 else ''}{pts}", CC_X + 20, cy, pts_col)
            cy += 34
            txt(screen, "h3", f"Total score:  {score}", CC_X + 20, cy, GOLD)

            btn(screen, r_continue, "CONTINUE  →",
                hover=hovered(r_continue), bg=(30, 50, 20), border=GREEN, fg=GREEN)

            pygame.display.flip()
            clock.tick(FPS)

            if clicked(events, r_continue):
                return

    # ── AUTOPLAY (chaos / revenge) ────────────────────────────────────────────
    def screen_autoplay(lines: list[str], title: str, color: tuple):
        idx = 0
        r_next = pygame.Rect(CC_X + 180, H - 90, 250, 50)
        r_skip = pygame.Rect(CC_X + 440, H - 90, 150, 50)

        while idx < len(lines):
            events = pygame.event.get()
            for ev in events:
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                    idx += 1

            screen.fill(BG)
            # Title
            txt(screen, "h2", title, CC_X + 10, 20, color)

            # Show last 12 lines, current line highlighted
            log_rect = pygame.Rect(CC_X + 10, 70, CC_W - 20, H - 200)
            box(screen, log_rect, bg=(10, 6, 2))
            visible  = lines[max(0, idx - 11): idx + 1]
            ly = log_rect.y + 10
            for j, line in enumerate(visible):
                is_current = (j == len(visible) - 1)
                col = (YELLOW if "SOUP NAZI" in line
                       else RED if "BANNED" in line or "NO SOUP" in line
                       else color if is_current
                       else LREY)
                fk = "body" if is_current else "small"
                ly = txt(screen, fk, line, log_rect.x + 10, ly, col,
                          max_w=log_rect.w - 20) + (6 if is_current else 2)

            btn(screen, r_next, "NEXT  [ ENTER ]", hover=hovered(r_next))
            btn(screen, r_skip, "SKIP ALL", hover=hovered(r_skip), bg=DGREY, fg=GREY)

            pygame.display.flip()
            clock.tick(FPS)

            if clicked(events, r_next): idx += 1
            if clicked(events, r_skip): break

    # ── END ───────────────────────────────────────────────────────────────────
    def screen_end(score: int, soups: int, bans: int, win: bool):
        r_again = pygame.Rect(CC_X + 100, H - 120, 200, 55)
        r_quit  = pygame.Rect(CC_X + 320, H - 120, 200, 55)
        while True:
            events = pygame.event.get()
            for ev in events:
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()

            screen.fill(BG)
            if win:
                txt(screen, "h1", "ALL SERVED!", CC_X + 60, 100, GREEN)
                txt(screen, "body", "The Soup Nazi nods. Once. Barely.", CC_X + 80, 170, CREAM)
            else:
                txt(screen, "h1", "NO SOUP FOR YOU!", CC_X + 20, 100, RED)
                txt(screen, "body", "Everyone got banned. Classic.", CC_X + 80, 170, CREAM)

            txt(screen, "h2", f"Final Score:  {score}", CC_X + 80, 230, GOLD)
            txt(screen, "body", f"Soups given: {soups}     Bans issued: {bans}", CC_X + 80, 280, LREY)

            btn(screen, r_again, "PLAY AGAIN", hover=hovered(r_again), bg=(20,40,20), border=GREEN, fg=GREEN)
            btn(screen, r_quit,  "QUIT",       hover=hovered(r_quit),  bg=DGREY, fg=GREY)

            pygame.display.flip()
            clock.tick(FPS)

            if clicked(events, r_again): return True
            if clicked(events, r_quit):  pygame.quit(); sys.exit()

    # ══════════════════════════════════════════════════════════════════════════
    # MAIN GAME LOOP
    # ══════════════════════════════════════════════════════════════════════════


    while True:
        choice = screen_title()

        if choice == "chaos":
            screen_autoplay(CHAOS_LINES, "[ CHAOS MODE ]", ORANGE)
            continue

        if choice == "revenge":
            screen_autoplay(REVENGE_LINES, "[ REVENGE MODE — Elaine Returns ]", (200, 100, 230))
            continue

        # ── Normal game ───────────────────────────────────────────────────────
        all_chars = make_characters()
        engine    = Engine()
        score     = 0
        log: list[str] = []

        def logit(s): log.append(s)

        remaining = [c for c in all_chars]  # chars not yet done

        while remaining:
            char = screen_char_select(remaining)

            logit(f"[ {char.name} steps up to the counter ]")
            logit(char_quip(char.name))

            # PREP — 15s menu study, no typing
            screen_prep(char, all_chars, score, engine, log)

            # Try up to 3 warnings
            done = False
            while not done:
                action   = screen_action(char, all_chars, score, engine, log)
                dialogue = screen_dialogue(char, all_chars, score, engine, log)

                raw, elapsed = screen_order(
                    char, all_chars, score, engine, log)

                result = engine.evaluate(char, raw, action, dialogue, elapsed)
                logit(result["message"])
                score += result["points"]

                if result["outcome"] == "soup":
                    logit(f"SOUP for {char.name}!  +{result['points']} pts")
                    char.got_soup = True
                elif result["outcome"] == "ban":
                    logit(f"{char.name} is BANNED.")
                    char.banned = True
                else:
                    logit(f"WARNING #{char.warnings}/3 for {char.name}.  {result['points']} pts")

                screen_result(result, char, all_chars, score, engine, log)
                done = char.got_soup or char.banned

            remaining = [c for c in all_chars if not c.got_soup and not c.banned]

        soups = sum(1 for c in all_chars if c.got_soup)
        bans  = sum(1 for c in all_chars if c.banned)
        win   = soups > 0

        again = screen_end(score, soups, bans, win)
        if not again:
            break


if __name__ == "__main__":
    run()
