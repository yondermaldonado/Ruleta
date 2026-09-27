"""
RULETA CASINO - Pygame
------------------------
Ruleta europea (0-36) con animaciones, sonidos generados por código
(sin archivos externos) y sistema de apuestas con saldo virtual.

Controles: usa el mouse para elegir ficha, tipo de apuesta y girar.

Para convertir a .exe (Windows), ver README.md incluido.
"""

import sys
import math
import random

import numpy as np
import pygame

# ----------------------------------------------------------------------
# CONFIGURACIÓN BÁSICA
# ----------------------------------------------------------------------
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ruleta Casino")
clock = pygame.time.Clock()

# Colores tema casino
GREEN_FELT   = (10, 70, 35)
GREEN_DARK   = (6, 45, 22)
GOLD         = (212, 175, 55)
GOLD_DARK    = (150, 120, 30)
RED          = (176, 30, 30)
BLACK_C      = (20, 20, 20)
WHITE        = (245, 245, 245)
GRAY         = (90, 90, 90)
TEXT_GREEN   = (40, 200, 90)
TEXT_RED     = (230, 60, 60)

FONT_TITLE = pygame.font.SysFont(None, 56, bold=True)
FONT_BIG   = pygame.font.SysFont(None, 40, bold=True)
FONT_MED   = pygame.font.SysFont(None, 28, bold=True)
FONT_SMALL = pygame.font.SysFont(None, 18, bold=True)
FONT_WHEEL = pygame.font.SysFont(None, 20, bold=True)

# ----------------------------------------------------------------------
# DATOS DE LA RULETA EUROPEA
# ----------------------------------------------------------------------
WHEEL_NUMBERS = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11,
                 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18,
                 29, 7, 28, 12, 35, 3, 26]
RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
N_SLOTS = len(WHEEL_NUMBERS)
ANGLE_PER_SLOT = 360 / N_SLOTS


def color_of(n):
    if n == 0:
        return (20, 130, 60)
    return RED if n in RED_NUMBERS else BLACK_C


# ----------------------------------------------------------------------
# SONIDOS GENERADOS POR CÓDIGO (no requieren archivos externos)
# ----------------------------------------------------------------------
SAMPLE_RATE = 44100


def make_tone(freq, duration, volume=0.5, wave="sine", decay=True):
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, False)
    if wave == "square":
        arr = np.sign(np.sin(2 * np.pi * freq * t))
    elif wave == "noise":
        arr = np.random.uniform(-1, 1, n)
    else:
        arr = np.sin(2 * np.pi * freq * t)
    if decay:
        env = np.linspace(1, 0, n) ** 1.4
        arr = arr * env
    audio = np.clip(arr * volume * 32767, -32767, 32767).astype(np.int16)
    stereo = np.column_stack([audio, audio])
    return pygame.sndarray.make_sound(np.ascontiguousarray(stereo))


tick_sound  = make_tone(1500, 0.025, 0.35, "square")
chip_sound  = make_tone(900, 0.06, 0.3, "sine")
lose_sound  = make_tone(140, 0.5, 0.5, "square")
click_sound = make_tone(700, 0.04, 0.25, "sine")
win_notes   = [make_tone(f, 0.16, 0.5, "sine") for f in (523, 659, 784, 1047)]

# ----------------------------------------------------------------------
# UTILIDADES GEOMÉTRICAS
# ----------------------------------------------------------------------
def point_on_circle(cx, cy, r, angle_deg):
    rad = math.radians(angle_deg)
    return (cx + r * math.sin(rad), cy - r * math.cos(rad))


def draw_text(surf, text, font, color, center):
    label = font.render(text, True, color)
    rect = label.get_rect(center=center)
    surf.blit(label, rect)


def draw_panel(surf, rect, color=GREEN_DARK, border=GOLD, radius=14, width=3):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    pygame.draw.rect(surf, border, rect, width, border_radius=radius)


class Button:
    def __init__(self, rect, text, font=FONT_MED, base=GOLD_DARK, hover=GOLD, text_color=BLACK_C):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.base = base
        self.hover = hover
        self.text_color = text_color
        self.selected = False

    def draw(self, surf, mouse_pos):
        color = self.hover if (self.rect.collidepoint(mouse_pos) or self.selected) else self.base
        pygame.draw.rect(surf, color, self.rect, border_radius=10)
        pygame.draw.rect(surf, GOLD, self.rect, 2, border_radius=10)
        draw_text(surf, self.text, self.font, self.text_color, self.rect.center)

    def clicked(self, pos, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(pos)


# ----------------------------------------------------------------------
# PRE-RENDER DE LA RUEDA (una sola vez, luego se rota como imagen)
# ----------------------------------------------------------------------
WHEEL_RADIUS = 210
SURF_SIZE = WHEEL_RADIUS * 2 + 20
base_wheel = pygame.Surface((SURF_SIZE, SURF_SIZE), pygame.SRCALPHA)
cx = cy = SURF_SIZE // 2

for i, num in enumerate(WHEEL_NUMBERS):
    angle_i = i * ANGLE_PER_SLOT
    half = ANGLE_PER_SLOT / 2
    points = [(cx, cy)]
    steps = 5
    for s in range(steps + 1):
        a = angle_i - half + (2 * half) * s / steps
        points.append(point_on_circle(cx, cy, WHEEL_RADIUS, a))
    pygame.draw.polygon(base_wheel, color_of(num), points)
    pygame.draw.polygon(base_wheel, GOLD_DARK, points, 1)

    label = FONT_WHEEL.render(str(num), True, WHITE)
    label = pygame.transform.rotate(label, -angle_i)
    lx, ly = point_on_circle(cx, cy, WHEEL_RADIUS * 0.83, angle_i)
    lrect = label.get_rect(center=(lx, ly))
    base_wheel.blit(label, lrect)

pygame.draw.circle(base_wheel, GOLD, (cx, cy), WHEEL_RADIUS, 5)
pygame.draw.circle(base_wheel, GOLD, (cx, cy), 34)
pygame.draw.circle(base_wheel, (90, 10, 10), (cx, cy), 26)
pygame.draw.circle(base_wheel, GOLD_DARK, (cx, cy), 26, 2)

WHEEL_CENTER = (260, 380)

# ----------------------------------------------------------------------
# ESTADO DEL JUEGO
# ----------------------------------------------------------------------
BET_TYPES = {
    "ROJO":  ("rojo",  2, RED),
    "NEGRO": ("negro", 2, BLACK_C),
    "PAR":   ("par",   2, GRAY),
    "IMPAR": ("impar", 2, GRAY),
    "VERDE": ("verde", 35, (20, 130, 60)),
}

state = "betting"      # betting | spinning | result | gameover
balance = 1000
bet_amount = 50
bet_type = None
message = ""
message_color = WHITE

wheel_rotation = 0.0
final_rotation = 0.0
spin_start = 0
SPIN_DURATION = 4200  # ms
last_slot_count = 0
winning_number = None
win_amount = 0
pending_jingle = []
jingle_next_time = 0

# --- Botones ---
chip_values = [10, 50, 100, 500]
chip_buttons = [Button((600 + idx * 90, 170, 78, 46), f"${v}") for idx, v in enumerate(chip_values)]

bet_buttons = {
    "ROJO":  Button((600, 250, 180, 46), "ROJO", base=(120, 20, 20), hover=RED, text_color=WHITE),
    "NEGRO": Button((790, 250, 180, 46), "NEGRO", base=(30, 30, 30), hover=(60, 60, 60), text_color=WHITE),
    "PAR":   Button((600, 306, 180, 46), "PAR"),
    "IMPAR": Button((790, 306, 180, 46), "IMPAR"),
    "VERDE": Button((600, 362, 370, 46), "VERDE (0) x35", base=(15, 90, 45), hover=(20, 130, 60), text_color=WHITE),
}

spin_button = Button((600, 440, 370, 64), "GIRAR", font=FONT_BIG, base=GOLD, hover=(240, 205, 90))
continue_button = Button((600, 440, 370, 64), "CONTINUAR", font=FONT_BIG, base=GOLD, hover=(240, 205, 90))
restart_button = Button((600, 440, 370, 64), "REINICIAR", font=FONT_BIG, base=GOLD, hover=(240, 205, 90))


def reset_round():
    global state, message
    state = "betting"
    message = ""


def start_spin():
    global state, spin_start, final_rotation, last_slot_count
    global winning_number, balance, pending_jingle, jingle_next_time

    if bet_type is None:
        return
    if bet_amount > balance:
        return

    balance -= bet_amount
    winning_number = random.randint(0, 36)
    winning_index = WHEEL_NUMBERS.index(winning_number)
    n_spins = random.randint(5, 8)
    target_angle = (-(winning_index * ANGLE_PER_SLOT)) % 360
    final_rotation = n_spins * 360 + target_angle

    spin_start = pygame.time.get_ticks()
    last_slot_count = 0
    pending_jingle = []
    jingle_next_time = 0
    state = "spinning"


def resolve_spin():
    global state, message, message_color, win_amount, balance, pending_jingle, jingle_next_time
    key, mult, _ = BET_TYPES[bet_type]
    if key == "rojo":
        won = winning_number in RED_NUMBERS
    elif key == "negro":
        won = winning_number != 0 and winning_number not in RED_NUMBERS
    elif key == "par":
        won = winning_number != 0 and winning_number % 2 == 0
    elif key == "impar":
        won = winning_number % 2 == 1
    else:  # verde
        won = winning_number == 0

    if won:
        win_amount = bet_amount * mult
        balance += win_amount
        message = f"¡GANASTE ${win_amount}!  Salió el {winning_number}"
        message_color = TEXT_GREEN
        pending_jingle = list(win_notes)
        jingle_next_time = pygame.time.get_ticks()
    else:
        win_amount = 0
        message = f"Perdiste. Salió el {winning_number}"
        message_color = TEXT_RED
        lose_sound.play()

    state = "gameover" if balance <= 0 else "result"


# ----------------------------------------------------------------------
# LOOP PRINCIPAL
# ----------------------------------------------------------------------
running = True
ball_angle = -90

while running:
    dt = clock.tick(60)
    now = pygame.time.get_ticks()
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "betting":
            for idx, btn in enumerate(chip_buttons):
                if btn.clicked(mouse_pos, event):
                    bet_amount = chip_values[idx]
                    chip_sound.play()
            for name, btn in bet_buttons.items():
                if btn.clicked(mouse_pos, event):
                    bet_type = name
                    click_sound.play()
            if spin_button.clicked(mouse_pos, event):
                if bet_type is not None and bet_amount <= balance:
                    click_sound.play()
                    start_spin()

        elif state == "result":
            if continue_button.clicked(mouse_pos, event):
                click_sound.play()
                reset_round()

        elif state == "gameover":
            if restart_button.clicked(mouse_pos, event):
                click_sound.play()
                balance = 1000
                reset_round()

    # --- lógica de giro ---
    if state == "spinning":
        elapsed = now - spin_start
        t = min(1.0, elapsed / SPIN_DURATION)
        eased = 1 - (1 - t) ** 3
        raw_rotation = eased * final_rotation
        wheel_rotation = raw_rotation % 360

        slot_count = raw_rotation / ANGLE_PER_SLOT
        if int(slot_count) > last_slot_count:
            last_slot_count = int(slot_count)
            tick_sound.play()

        ball_angle = -90 - (1 - eased) * 720

        if t >= 1.0:
            resolve_spin()

    # reproducir jingle de victoria en cascada
    if pending_jingle and now >= jingle_next_time:
        note = pending_jingle.pop(0)
        note.play()
        jingle_next_time = now + 140

    # ------------------------------------------------------------------
    # DIBUJO
    # ------------------------------------------------------------------
    screen.fill(GREEN_DARK)
    pygame.draw.rect(screen, GREEN_FELT, (10, 10, WIDTH - 20, HEIGHT - 20), border_radius=24)
    pygame.draw.rect(screen, GOLD, (10, 10, WIDTH - 20, HEIGHT - 20), 4, border_radius=24)

    draw_text(screen, "CASINO ROULETTE", FONT_TITLE, GOLD, (WIDTH // 2, 46))
    draw_text(screen, f"Saldo: ${balance}", FONT_MED, WHITE, (150, 100))

    # rueda
    rotated = pygame.transform.rotate(base_wheel, -wheel_rotation)
    rrect = rotated.get_rect(center=WHEEL_CENTER)
    screen.blit(rotated, rrect)

    # pelota
    if state == "spinning" or (state in ("result", "gameover") and winning_number is not None):
        angle_for_ball = ball_angle if state == "spinning" else -90
        bx, by = point_on_circle(WHEEL_CENTER[0], WHEEL_CENTER[1], WHEEL_RADIUS - 18, angle_for_ball)
        pygame.draw.circle(screen, WHITE, (int(bx), int(by)), 8)
        pygame.draw.circle(screen, GRAY, (int(bx), int(by)), 8, 1)

    # puntero fijo arriba de la rueda
    px, py = WHEEL_CENTER[0], WHEEL_CENTER[1] - WHEEL_RADIUS - 14
    pygame.draw.polygon(screen, GOLD, [(px - 12, py - 18), (px + 12, py - 18), (px, py + 6)])

    # panel derecho
    if state == "betting":
        draw_panel(screen, (590, 120, 390, 300))
        draw_text(screen, "Elige tu ficha", FONT_SMALL, WHITE, (785, 145))
        for btn in chip_buttons:
            btn.selected = (bet_amount == int(btn.text[1:]))
            btn.draw(screen, mouse_pos)

        draw_text(screen, "Elige tu apuesta", FONT_SMALL, WHITE, (785, 232))
        for name, btn in bet_buttons.items():
            btn.selected = (bet_type == name)
            btn.draw(screen, mouse_pos)

        draw_text(screen, f"Apuesta actual: ${bet_amount}", FONT_SMALL, GOLD, (785, 405))

        spin_button.draw(screen, mouse_pos)
        if bet_type is None:
            draw_text(screen, "Selecciona un tipo de apuesta", FONT_SMALL, TEXT_RED, (785, 520))
        elif bet_amount > balance:
            draw_text(screen, "Saldo insuficiente", FONT_SMALL, TEXT_RED, (785, 520))

    elif state == "spinning":
        draw_panel(screen, (590, 120, 390, 300))
        draw_text(screen, "Girando...", FONT_BIG, GOLD, (785, 280))

    elif state == "result":
        draw_panel(screen, (590, 120, 390, 300))
        draw_text(screen, f"Número: {winning_number}", FONT_BIG, WHITE, (785, 220))
        draw_text(screen, message, FONT_MED, message_color, (785, 280))
        draw_text(screen, f"Saldo: ${balance}", FONT_MED, WHITE, (785, 330))
        continue_button.draw(screen, mouse_pos)

    elif state == "gameover":
        draw_panel(screen, (590, 120, 390, 300))
        draw_text(screen, "SIN SALDO", FONT_BIG, TEXT_RED, (785, 230))
        draw_text(screen, f"Número: {winning_number}", FONT_MED, WHITE, (785, 280))
        draw_text(screen, message, FONT_SMALL, message_color, (785, 320))
        restart_button.draw(screen, mouse_pos)

    pygame.display.flip()

pygame.quit()
sys.exit()
