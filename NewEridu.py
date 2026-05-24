import pygame
import math

pygame.init()

WIDTH = 1200
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini NukeMap")

clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 30)
small_font = pygame.font.SysFont(None, 22)

# carica mappa
original_map = pygame.image.load("map.png").convert()

# zoom
zoom = 1.0
min_zoom = 0.5
max_zoom = 5.0

# offset camera
offset_x = 0
offset_y = 0

# lista esplosioni
explosions = []

# stato input esplosione
input_mode = False
input_text = ""
pending_position = None


class Explosion:
    def __init__(self, x, y, power_kilotons):
        self.x = x
        self.y = y
        self.power = power_kilotons

        # scala: 1 pixel = 24 km
        scale = 1 / 24

        # modelli semplificati (in pixel mondo)
        self.fireball = (power_kilotons ** 0.4) * 3 * scale
        self.shockwave = (power_kilotons ** 0.33) * 8 * scale
        self.thermal = (power_kilotons ** 0.5) * 12 * scale
        
        # NUOVO: fallout radioattivo (più grande, diffusivo)
        self.fallout = (power_kilotons ** 0.6) * 25 * scale

    def draw(self, surface):

        sx = int(self.x * zoom + offset_x)
        sy = int(self.y * zoom + offset_y)

        fireball = int(self.fireball * zoom)
        shockwave = int(self.shockwave * zoom)
        thermal = int(self.thermal * zoom)
        fallout = int(self.fallout * zoom)

        # fallout (verde, più esterno)
        pygame.draw.circle(surface, (0, 255, 0), (sx, sy), fallout, 2)

        # thermal
        pygame.draw.circle(surface, (255, 255, 0), (sx, sy), thermal, 2)

        # shockwave
        pygame.draw.circle(surface, (255, 0, 0), (sx, sy), shockwave, 2)

        # fireball
        pygame.draw.circle(surface, (255, 120, 0), (sx, sy), fireball)


def draw_legend(surface):
    x, y = 20, HEIGHT - 140

    legend_items = [
        ("Fireball", (255, 120, 0)),
        ("Shockwave", (255, 0, 0)),
        ("Thermal radiation", (255, 255, 0)),
        ("Fallout radioattivo", (0, 255, 0)),
    ]

    for i, (text, color) in enumerate(legend_items):
        pygame.draw.rect(surface, color, (x, y + i * 25, 15, 15))
        label = small_font.render(text, True, (255, 255, 255))
        surface.blit(label, (x + 25, y + i * 25 - 2))


running = True

while running:

    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                explosions.clear()

            if input_mode:
                if event.key == pygame.K_RETURN:
                    try:
                        power = float(input_text)

                        if pending_position:
                            explosions.append(
                                Explosion(
                                    pending_position[0],
                                    pending_position[1],
                                    power
                                )
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

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 4 or event.button == 5:

                mx, my = pygame.mouse.get_pos()

                world_x = (mx - offset_x) / zoom
                world_y = (my - offset_y) / zoom

                if event.button == 4:
                    zoom *= 1.1
                else:
                    zoom /= 1.1

                zoom = max(min_zoom, min(max_zoom, zoom))

                offset_x = mx - world_x * zoom
                offset_y = my - world_y * zoom

            elif event.button == 1 and not input_mode:

                mx, my = pygame.mouse.get_pos()

                world_x = (mx - offset_x) / zoom
                world_y = (my - offset_y) / zoom

                pending_position = (world_x, world_y)
                input_mode = True
                input_text = ""

    map_width = int(original_map.get_width() * zoom)
    map_height = int(original_map.get_height() * zoom)

    scaled_map = pygame.transform.smoothscale(original_map, (map_width, map_height))

    screen.fill((0, 0, 0))
    screen.blit(scaled_map, (offset_x, offset_y))

    for exp in explosions:
        exp.draw(screen)

    draw_legend(screen)

    if input_mode:
        pygame.draw.rect(screen, (0, 0, 0), (300, 300, 600, 100))
        pygame.draw.rect(screen, (255, 255, 255), (300, 300, 600, 100), 2)

        txt = font.render("Kilotoni: " + input_text, True, (255, 255, 255))
        screen.blit(txt, (320, 340))

    pygame.display.flip()

pygame.quit()