import pygame
import math

pygame.init()

WIDTH = 1200
HEIGHT = 700

FOGGIA_X = 953
FOGGIA_Y = 277

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini NukeMap")

clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 30)
small_font = pygame.font.SysFont(None, 22)

# carica mappa
original_map = pygame.image.load("map.png").convert()

# -----------------------------
# ZOOM (VINCOLATO ALLA FINESTRA)
# -----------------------------
map_w = original_map.get_width()
map_h = original_map.get_height()

fit_zoom = max(WIDTH / map_w, HEIGHT / map_h)

zoom = fit_zoom
min_zoom = fit_zoom
max_zoom = 5.0

# offset camera
offset_x = 0
offset_y = 0

# DRAG PAN
dragging = False
last_mouse = None

# lista esplosioni
explosions = []

# input manuale
input_mode = False
input_text = ""
pending_position = None

# -----------------------------
# PRESET BOMBE (KILOTONI)
# -----------------------------
bomb_presets = {
    "Custom": None,
    "Little Boy": 15,
    "Fat Man": 21,
    "Trinity": 20,
    "Ivy Mike": 10400,
    "Castle Bravo": 15000,
    "Tsar Bomba": 50000,
    "W88": 475,
    "B83": 1200,
}

selected_preset = "Custom"
preset_keys = list(bomb_presets.keys())


class Explosion:
    def __init__(self, x, y, power_kilotons):
        self.x = x
        self.y = y
        self.power = power_kilotons

        scale = 1 / 24

        self.fireball = (power_kilotons ** 0.4) * 3 * scale
        self.shockwave = (power_kilotons ** 0.33) * 8 * scale
        self.thermal = (power_kilotons ** 0.5) * 12 * scale
        self.fallout = (power_kilotons ** 0.6) * 25 * scale

    def draw(self, surface):

        sx = int(self.x * zoom + offset_x)
        sy = int(self.y * zoom + offset_y)

        pygame.draw.circle(surface, (0, 255, 0), (sx, sy), int(self.fallout * zoom), 2)
        pygame.draw.circle(surface, (255, 255, 0), (sx, sy), int(self.thermal * zoom), 2)
        pygame.draw.circle(surface, (255, 0, 0), (sx, sy), int(self.shockwave * zoom), 2)
        pygame.draw.circle(surface, (255, 120, 0), (sx, sy), int(self.fireball * zoom))


def draw_legend(surface):
    x, y = 20, HEIGHT - 140

    legend_items = [
        ("Palla di fuoco", (255, 120, 0)),
        ("Onda d'urto", (255, 0, 0)),
        ("Radiazione termica", (255, 255, 0)),
        ("Fallout radioattivo", (0, 255, 0)),
    ]

    for i, (text, color) in enumerate(legend_items):
        pygame.draw.rect(surface, color, (x, y + i * 25, 15, 15))
        label = small_font.render(text, True, (0, 0, 0))
        surface.blit(label, (x + 25, y + i * 25 - 2))


def draw_controls(surface):
    x, y = 20, 20

    controls = [
        "CLICK: piazza esplosione",
        "RUOTA MOUSE: zoom",
        "TASTO DESTRO: trascina mappa",
        "TAB: cambia preset",
        "C: cancella esplosioni",
    ]

    for i, text in enumerate(controls):
        label = small_font.render(text, True, (0, 0, 0))
        surface.blit(label, (x, y + i * 20))


def draw_presets(surface):
    start_x = WIDTH - 220
    start_y = 20

    for i, name in enumerate(preset_keys):
        rect = pygame.Rect(start_x, start_y + i * 28, 200, 24)

        is_selected = (name == selected_preset)
        color = (80, 80, 80) if not is_selected else (200, 80, 80)

        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (255, 255, 255), rect, 1)

        label = small_font.render(name, True, (255, 255, 255))
        surface.blit(label, (start_x + 8, start_y + i * 28 + 4))


running = True

while running:

    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # -------------------------
        # MOUSE BUTTON DOWN
        # -------------------------
        if event.type == pygame.MOUSEBUTTONDOWN:

            mx, my = pygame.mouse.get_pos()

            # ZOOM
            if event.button in (4, 5):
                world_x = (mx - offset_x) / zoom
                world_y = (my - offset_y) / zoom

                if event.button == 4:
                    zoom *= 1.1
                else:
                    zoom /= 1.1

                zoom = max(min_zoom, min(max_zoom, zoom))

                offset_x = mx - world_x * zoom
                offset_y = my - world_y * zoom

            # TASTO DESTRO -> INIZIA DRAG
            elif event.button == 3:
                dragging = True
                last_mouse = (mx, my)

            # CLICK SINISTRO
            elif event.button == 1:

                start_x = WIDTH - 220
                start_y = 20

                clicked_preset = None

                for i, name in enumerate(preset_keys):
                    rect = pygame.Rect(start_x, start_y + i * 28, 200, 24)
                    if rect.collidepoint(mx, my):
                        clicked_preset = name
                        break

                if clicked_preset:
                    selected_preset = clicked_preset
                    continue

                world_x = (mx - offset_x) / zoom
                world_y = (my - offset_y) / zoom

                power = bomb_presets[selected_preset]

                if power is None:
                    pending_position = (world_x, world_y)
                    input_mode = True
                    input_text = ""
                else:
                    explosions.append(Explosion(world_x, world_y, power))

        # -------------------------
        # MOUSE BUTTON UP
        # -------------------------
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:
                dragging = False
                last_mouse = None

        # -------------------------
        # MOUSE MOVE (DRAG MAPPA)
        # -------------------------
        if event.type == pygame.MOUSEMOTION and dragging:

            mx, my = event.pos
            lx, ly = last_mouse

            dx = mx - lx
            dy = my - ly

            offset_x += dx
            offset_y += dy

            last_mouse = (mx, my)

        # -------------------------
        # KEYBOARD
        # -------------------------
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_c:
                explosions.clear()

            if event.key == pygame.K_TAB:
                idx = preset_keys.index(selected_preset)
                selected_preset = preset_keys[(idx + 1) % len(preset_keys)]

            if input_mode:
                if event.key == pygame.K_RETURN:
                    try:
                        power = float(input_text)

                        if pending_position:
                            explosions.append(
                                Explosion(pending_position[0], pending_position[1], power)
                            )
                    except:
                        pass

                    input_mode = False
                    input_text = ""
                    pending_position = None

                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]

                else:
                    if event.unicode.isdigit() or event.unicode == ".":
                        input_text += event.unicode
            if event.key == pygame.K_f:
                power = bomb_presets[selected_preset]
                if power is None:
                    power = 100  # kilotoni di default
                explosions.append(Explosion(FOGGIA_X, FOGGIA_Y, power))

    # -----------------------------
    # RENDER MAPPA
    # -----------------------------
    map_width = int(map_w * zoom)
    map_height = int(map_h * zoom)

    scaled_map = pygame.transform.smoothscale(original_map, (map_width, map_height))

    screen.fill((0, 0, 0))
    screen.blit(scaled_map, (offset_x, offset_y))

    for exp in explosions:
        exp.draw(screen)

    draw_controls(screen)
    draw_legend(screen)
    draw_presets(screen)

    if input_mode:
        pygame.draw.rect(screen, (0, 0, 0), (300, 300, 600, 100))
        pygame.draw.rect(screen, (255, 255, 255), (300, 300, 600, 100), 2)

        txt = font.render("Kilotoni: " + input_text, True, (255, 255, 255))
        screen.blit(txt, (320, 340))

    pygame.display.flip()

pygame.quit()