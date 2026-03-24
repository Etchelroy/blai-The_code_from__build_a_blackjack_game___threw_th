import pygame
import random
import sys
import math

pygame.init()

# ── Constants ──────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1100, 750
FPS = 60

# Colours
GREEN_FELT  = (34,  85,  34)
DARK_GREEN  = (20,  60,  20)
GOLD        = (212, 175,  55)
WHITE       = (255, 255, 255)
BLACK       = (  0,   0,   0)
RED         = (200,  30,  30)
BLUE        = ( 30,  30, 200)
LIGHT_GREY  = (200, 200, 200)
DARK_GREY   = ( 80,  80,  80)
YELLOW      = (255, 215,   0)
ORANGE      = (230, 140,  20)

# Card geometry
CARD_W, CARD_H = 72, 108
CARD_RADIUS    = 8

# ── Fonts ──────────────────────────────────────────────────────────────────────
pygame.font.init()
FONT_LG  = pygame.font.SysFont("segoeui", 36, bold=True)
FONT_MD  = pygame.font.SysFont("segoeui", 26, bold=True)
FONT_SM  = pygame.font.SysFont("segoeui", 20)
FONT_XSM = pygame.font.SysFont("segoeui", 16)

# ── Deck helpers ───────────────────────────────────────────────────────────────
SUITS  = ["S", "H", "D", "C"]
SUIT_SYMBOLS = {"S": "♠", "H": "♥", "D": "♦", "C": "♣"}
RANKS  = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
VALUES = {"A":11,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,
          "8":8,"9":9,"10":10,"J":10,"Q":10,"K":10}

def build_deck(num_decks=6):
    deck = []
    for _ in range(num_decks):
        for s in SUITS:
            for r in RANKS:
                deck.append((r, s))
    random.shuffle(deck)
    return deck

def hand_value(hand):
    total, aces = 0, 0
    for rank, _ in hand:
        total += VALUES[rank]
        if rank == "A":
            aces += 1
    while total > 21 and aces:
        total -= 10
        aces  -= 1
    return total

def is_bust(hand):
    return hand_value(hand) > 21

def is_blackjack(hand):
    return len(hand) == 2 and hand_value(hand) == 21

# ── Card drawing ───────────────────────────────────────────────────────────────
def card_color(suit):
    return RED if suit in ("H", "D") else BLACK

def draw_card(surface, card, x, y, face_down=False):
    rect = pygame.Rect(x, y, CARD_W, CARD_H)
    # Shadow
    shadow_surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 80),
                     pygame.Rect(0, 0, CARD_W, CARD_H), border_radius=CARD_RADIUS)
    surface.blit(shadow_surf, (x + 4, y + 4))

    # Card face
    bg_color = WHITE if not face_down else DARK_GREY
    pygame.draw.rect(surface, bg_color, rect, border_radius=CARD_RADIUS)
    pygame.draw.rect(surface, BLACK, rect, 2, border_radius=CARD_RADIUS)

    if face_down:
        for i in range(0, CARD_W + CARD_H, 12):
            sx1 = x + i
            sy1 = y
            ex1 = x
            ey1 = y + i
            if sx1 > x + CARD_W:
                sx1 = x + CARD_W
            if ey1 > y + CARD_H:
                ey1 = y + CARD_H
            pygame.draw.line(surface, DARK_GREEN, (sx1, sy1), (ex1, ey1), 1)
        return

    rank, suit = card
    sym = SUIT_SYMBOLS[suit]
    color = card_color(suit)

    r_surf = FONT_XSM.render(rank, True, color)
    s_surf = FONT_XSM.render(sym, True, color)
    surface.blit(r_surf, (x + 4, y + 2))
    surface.blit(s_surf, (x + 4, y + 2 + r_surf.get_height()))

    big = FONT_LG.render(sym, True, color)
    bx  = x + CARD_W // 2 - big.get_width() // 2
    by  = y + CARD_H // 2 - big.get_height() // 2
    surface.blit(big, (bx, by))

    r2 = FONT_XSM.render(rank, True, color)
    s2 = FONT_XSM.render(sym, True, color)
    surface.blit(r2, (x + CARD_W - r2.get_width() - 4,
                      y + CARD_H - r2.get_height() - s2.get_height() - 2))
    surface.blit(s2, (x + CARD_W - s2.get_width() - 4,
                      y + CARD_H - s2.get_height() - 2))

def draw_hand(surface, hand, start_x, y, hide_second=False):
    for i, card in enumerate(hand):
        face_down = (hide_second and i == 1)
        draw_card(surface, card, start_x + i * (CARD_W + 8), y, face_down)

def hand_start_x(num_cards, center_x=SCREEN_W // 2):
    total_w = num_cards * CARD_W + (num_cards - 1) * 8
    return center_x - total_w // 2

# ── Button ─────────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, x, y, w, h, label,
                 color=DARK_GREY, hover_color=GOLD, text_color=WHITE):
        self.rect        = pygame.Rect(x, y, w, h)
        self.label       = label
        self.color       = color
        self.hover_color = hover_color
        self.text_color  = text_color
        self.hovered     = False
        self.enabled     = True

    def draw(self, surface):
        if not self.enabled:
            col = (60, 60, 60)
        elif self.hovered:
            col = self.hover_color
        else:
            col = self.color
        pygame.draw.rect(surface, col, self.rect, border_radius=10)
        pygame.draw.rect(surface, GOLD, self.rect, 2, border_radius=10)
        txt_color = self.text_color if self.enabled else DARK_GREY
        txt = FONT_SM.render(self.label, True, txt_color)
        surface.blit(txt, (self.rect.centerx - txt.get_width() // 2,
                           self.rect.centery - txt.get_height() // 2))

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos):
        return self.enabled and self.rect.collidepoint(pos)

# ── Chip ───────────────────────────────────────────────────────────────────────
class Chip:
    DENOM = {5: RED, 25: BLUE, 100: BLACK, 500: ORANGE}

    def __init__(self, value, cx, cy):
        self.value  = value
        self.cx     = cx
        self.cy     = cy
        self.radius = 24
        self.rect   = pygame.Rect(cx - self.radius, cy - self.radius,
                                  self.radius * 2, self.radius * 2)

    def draw(self, surface):
        color = self.DENOM.get(self.value, DARK_GREY)
        pygame.draw.circle(surface, color, (self.cx, self.cy), self.radius)
        pygame.draw.circle(surface, WHITE, (self.cx, self.cy), self.radius, 2)
        for deg in range(0, 360, 30):
            rad = math.radians(deg)
            ix  = int(self.cx + (self.radius - 5) * math.cos(rad))
            iy  = int(self.cy + (self.radius - 5) * math.sin(rad))
            ox  = int(self.cx + self.radius * math.cos(rad))
            oy  = int(self.cy + self.radius * math.sin(rad))
            pygame.draw.line(surface, WHITE, (ix, iy), (ox, oy), 2)
        label = FONT_XSM.render("$" + str(self.value), True, WHITE)
        surface.blit(label, (self.cx - label.get_width() // 2,
                              self.cy - label.get_height() // 2))

    def is_clicked(self, pos):
        dx = pos[0] - self.cx
        dy = pos[1] - self.cy
        return (dx * dx + dy * dy) <= self.radius ** 2

# ── Main Game ──────────────────────────────────────────────────────────────────
class BlackjackGame:

    def __init__(self):
        self.screen  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Blackjack")
        self.clock   = pygame.time.Clock()

        self.balance      = 1000
        self.bet          = 0
        self._last_bet    = 0
        self.deck         = build_deck()

        self.player_hand  = []
        self.dealer_hand  = []
        self.player_hands = []
        self.active_hand  = 0
        self.split_bets   = []

        self.state        = "betting"
        self.result_msg   = ""
        self.show_dealer  = False

        self.dealer_timer = 0
        self.dealer_delay = 900

        self._new_btn_rect = None
        self._build_ui()

    # ── UI construction ────────────────────────────────────────────────────────
    def _build_ui(self):
        bx = SCREEN_W // 2
        by = SCREEN_H - 70
        bw = 110
        bh = 44

        self.btn_hit    = Button(bx - 230, by, bw, bh, "Hit",    color=(30, 120, 30))
        self.btn_stand  = Button(bx - 110, by, bw, bh, "Stand",  color=(140, 30, 30))
        self.btn_double = Button(bx + 5,   by, bw, bh, "Double", color=(20, 80, 160))
        self.btn_split  = Button(bx + 120, by, bw, bh, "Split",  color=(120, 60, 160))

        self.btn_deal   = Button(bx - 55,  by, 110, bh, "Deal",   color=(30, 120, 30))
        self.btn_clear  = Button(bx + 65,  by, 110, bh, "Clear",  color=(140, 30, 30))
        self.btn_rebet  = Button(bx - 175, by, 110, bh, "Re-Bet", color=(20, 80, 160))

        self.chips = [
            Chip(5,   SCREEN_W // 2 - 180, SCREEN_H - 155),
            Chip(25,  SCREEN_W // 2 -  90, SCREEN_H - 155),
            Chip(100, SCREEN_W // 2,        SCREEN_H - 155),
            Chip(500, SCREEN_W // 2 +  90, SCREEN_H - 155),
        ]

    # ── Deck ───────────────────────────────────────────────────────────────────
    def _draw_card(self):
        if len(self.deck) < 20:
            self.deck = build_deck()
        return self.deck.pop()

    # ── Betting ────────────────────────────────────────────────────────────────
    def add_bet(self, amount):
        if self.state != "betting":
            return
        if amount <= self.balance:
            self.bet     += amount
            self.balance -= amount

    def clear_bet(self):
        if self.state != "betting":
            return
        self.balance += self.bet
        self.bet      = 0

    def rebet(self, amount):
        if self.state != "betting":
            return
        self.clear_bet()
        if amount > 0 and amount <= self.balance:
            self.bet     = amount
            self.balance -= amount

    # ── Deal ───────────────────────────────────────────────────────────────────
    def deal(self):
        if self.bet == 0 or self.state != "betting":
            return
        self.player_hand  = [self._draw_card(), self._draw_card()]
        self.dealer_hand  = [self._draw_card(), self._draw_card()]
        self.player_hands = [self.player_hand]
        self.split_bets   = [self.bet]
        self.active_hand  = 0
        self.show_dealer  = False
        self.result_msg   = ""

        if is_blackjack(self.player_hand):
            self.show_dealer = True
            if is_blackjack(self.dealer_hand):
                self.result_msg = "Push -- both Blackjack!"
                self.balance   += self.bet
            else:
                winnings        = int(self.bet * 2.5)
                self.result_msg = "Blackjack!  +$" + str(winnings - self.bet)
                self.balance   += winnings
            self.bet   = 0
            self.state = "round_over"
        else:
            self.state = "player_turn"

    # ── Player actions ─────────────────────────────────────────────────────────
    def _current_hand(self):
        if self.active_hand < len(self.player_hands):
            return self.player_hands[self.active_hand]
        return []

    def hit(self):
        if self.state != "player_turn":
            return
        hand = self._current_hand()
        hand.append(self._draw_card())
        if is_bust(hand):
            self._next_hand_or_dealer()

    def stand(self):
        if self.state != "player_turn":
            return
        self._next_hand_or_dealer()

    def double_down(self):
        if self.state != "player_turn":
            return
        hand = self._current_hand()
        if len(hand) != 2:
            return
        extra = min(self.split_bets[self.active_hand], self.balance)
        self.balance                      -= extra
        self.split_bets[self.active_hand] += extra
        hand.append(self._draw_card())
        self._next_hand_or_dealer()

    def split(self):
        if self.state != "player_turn":
            return
        hand = self._current_hand()
        if len(hand) != 2 or hand[0][0] != hand[1][0]:
            return
        bet = self.split_bets[self.active_hand]
        if bet > self.balance:
            return
        self.balance -= bet
        new_hand      = [hand.pop()]
        hand.append(self._draw_card())
        new_hand.append(self._draw_card())
        self.player_hands.insert(self.active_hand + 1, new_hand)
        self.split_bets.insert(self.active_hand + 1, bet)

    def _next_hand_or_dealer(self):
        self.active_hand += 1
        if self.active_hand >= len(self.player_hands):
            any_alive = any(not is_bust(h) for h in self.player_hands)
            if any_alive:
                self.state        = "dealer_turn"
                self.show_dealer  = True
                self.dealer_timer = pygame.time.get_ticks()
            else:
                self._finish_round()

    # ── Dealer turn ────────────────────────────────────────────────────────────
    def dealer_step(self):
        if hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(self._draw_card())
        else:
            self._finish_round()

    # ── Resolve ────────────────────────────────────────────────────────────────
    def _finish_round(self):
        self.show_dealer = True
        dv           = hand_value(self.dealer_hand)
        dealer_bust  = is_bust(self.dealer_hand)
        results      = []

        for i, hand in enumerate(self.player_hands):
            pv  = hand_value(hand)
            bet = self.split_bets[i]
            if is_bust(hand):
                results.append("Bust")
            elif dealer_bust or pv > dv:
                self.balance += bet * 2
                results.append("+$" + str(bet))
            elif pv == dv:
                self.balance += bet
                results.append("Push")
            else:
                results.append("-$" + str(bet))

        self.result_msg = "   |   ".join(results)
        self.bet        = 0
        self.state      = "round_over"

    # ── New round ──────────────────────────────────────────────────────────────
    def new_round(self):
        self.player_hand   = []
        self.dealer_hand   = []
        self.player_hands  = []
        self.split_bets    = []
        self.active_hand   = 0
        self.bet           = 0
        self.show_dealer   = False
        self.result_msg    = ""
        self._new_btn_rect = None
        self.state         = "betting"
        if self.balance <= 0:
            self.balance = 1000

    # ── Update ─────────────────────────────────────────────────────────────────
    def update(self):
        if self.state == "dealer_turn":
            now = pygame.time.get_ticks()
            if now - self.dealer_timer >= self.dealer_delay:
                self.dealer_timer = now
                self.dealer_step()

    # ── Draw helpers ───────────────────────────────────────────────────────────
    def _draw_felt(self):
        self.screen.fill(GREEN_FELT)
        oval = pygame.Rect(40, 20, SCREEN_W - 80, SCREEN_H - 220)
        pygame.draw.ellipse(self.screen, DARK_GREEN, oval)
        pygame.draw.ellipse(self.screen, GOLD, oval, 4)
        title = FONT_LG.render("  B L A C K J A C K  ", True, GOLD)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 28))

    def _draw_balance_bet(self):
        bal_surf = FONT_MD.render("Balance: $" + str(self.balance), True, WHITE)
        bet_surf = FONT_MD.render("Bet: $" + str(self.bet),         True, YELLOW)
        self.screen.blit(bal_surf, (30, SCREEN_H - 50))
        self.screen.blit(bet_surf, (30, SCREEN_H - 80))

    def _draw_score(self, hand, cx, y, label, hide=False):
        if not hand:
            return
        if hide:
            v_str = str(hand_value([hand[0]])) + " + ?"
        else:
            v_str = str(hand_value(hand))
        lbl = FONT_SM.render(label + ": " + v_str, True, WHITE)
        self.screen.blit(lbl, (cx - lbl.get_width() // 2, y))

    def _draw_result(self):
        if not self.result_msg:
            return
        overlay = pygame.Surface((700, 70), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (SCREEN_W // 2 - 350, SCREEN_H // 2 - 35))
        msg = FONT_LG.render(self.result_msg, True, YELLOW)
        self.screen.blit(msg, (SCREEN_W // 2 - msg.get_width() // 2,
                               SCREEN_H // 2 - msg.get_height() // 2))

    def _draw_buttons(self):
        if self.state == "betting":
            for chip in self.chips:
                chip.draw(self.screen)
            self.btn_deal.enabled  = self.bet > 0
            self.btn_clear.enabled = self.bet > 0
            self.btn_rebet.enabled = self.balance > 0 and self._last_bet > 0
            self.btn_deal.draw(self.screen)
            self.btn_clear.draw(self.screen)
            self.btn_rebet.draw(self.screen)

        elif self.state == "player_turn":
            hand    = self._current_hand()
            can_dbl = (len(hand) == 2 and
                       self.split_bets[self.active_hand] <= self.balance)
            can_spl = (len(hand) == 2 and
                       hand[0][0] == hand[1][0] and
                       self.split_bets[self.active_hand] <= self.balance)
            self.btn_double.enabled = can_dbl
            self.btn_split.enabled  = can_spl
            self.btn_hit.draw(self.screen)
            self.btn_stand.draw(self.screen)
            self.btn_double.draw(self.screen)
            self.btn_split.draw(self.screen)

        elif self.state == "round_over":
            new_btn = Button(SCREEN_W // 2 - 80, SCREEN_H - 70,
                             160, 44, "New Round", color=(30, 120, 30))
            new_btn.draw(self.screen)
            self._new_btn_rect = new_btn.rect

    def _draw_hands(self):
        if self.dealer_hand:
            dx = hand_start_x(len(self.dealer_hand))
            draw_hand(self.screen, self.dealer_hand, dx, 120,
                      hide_second=not self.show_dealer)
            self._draw_score(self.dealer_hand, SCREEN_W // 2, 92,
                             "Dealer", hide=not self.show_dealer)

        if self.player_hands:
            n      = len(self.player_hands)
            slot_w = SCREEN_W // (n + 1)
            for i, hand in enumerate(self.player_hands):
                cx = slot_w * (i + 1)
                hx = hand_start_x(len(hand), cx)
                hy = SCREEN_H - 340
                if self.state == "player_turn" and i == self.active_hand:
                    mark = pygame.Rect(hx - 6, hy - 6,
                                       len(hand) * (CARD_W + 8) + 2,
                                       CARD_H + 12)
                    pygame.draw.rect(self.screen, GOLD, mark, 3,
                                     border_radius=10)
                draw_hand(self.screen, hand, hx, hy)
                label = "You" if n == 1 else ("Hand " + str(i + 1))
                if is_bust(hand):
                    label += " BUST"
                self._draw_score(hand, cx, hy - 28, label)

    # ── Main draw ──────────────────────────────────────────────────────────────
    def draw(self):
        self._draw_felt()
        self._draw_hands()
        self._draw_balance_bet()
        self._draw_buttons()
        self._draw_result()
        pygame.display.flip()

    # ── Event handling ─────────────────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            for btn in [self.btn_hit, self.btn_stand, self.btn_double,
                        self.btn_split, self.btn_deal, self.btn_clear,
                        self.btn_rebet]:
                btn.check_hover(pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if self.state == "betting":
                for chip in self.chips:
                    if chip.is_clicked(pos):
                        self.add_bet(chip.value)
                if self.btn_deal.is_clicked(pos):
                    self._last_bet = self.bet
                    self.deal()
                elif self.btn_clear.is_clicked(pos):
                    self.clear_bet()
                elif self.btn_rebet.is_clicked(pos):
                    self.rebet(self._last_bet)

            elif self.state == "player_turn":
                if self.btn_hit.is_clicked(pos):
                    self.hit()
                elif self.btn_stand.is_clicked(pos):
                    self.stand()
                elif self.btn_double.is_clicked(pos):
                    self.double_down()
                elif self.btn_split.is_clicked(pos):
                    self.split()

            elif self.state == "round_over":
                rect = self._new_btn_rect
                if rect and rect.collidepoint(pos):
                    self.new_round()

    # ── Run ────────────────────────────────────────────────────────────────────
    def run(self):
        while True:
            for event in pygame.event.get():
                self.handle_event(event)
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    BlackjackGame().run()