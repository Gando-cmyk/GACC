import pygame
import math

pygame.init()

WIDTH = 1200
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini NukeMap")

clock = pygame.time.Clock()

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

class Explosion:
    def __init__(self, x, y, power):
        # coordinate mondo
        self.x = x
        self.y = y
        self.power = power

        # raggi
        self.fireball = power * 2
        self.shockwave = power * 5
        self.thermal = power * 8

    def draw(self, surface):

        # converte coordinate mondo -> schermo
        sx = int(self.x * zoom + offset_x)
        sy = int(self.y * zoom + offset_y)

        # raggi scalati con zoom
        fireball = int(self.fireball * zoom)
        shockwave = int(self.shockwave * zoom)
        thermal = int(self.thermal * zoom)

        # termico
        pygame.draw.circle(
            surface,
            (255, 120, 0),
            (sx, sy),
            thermal,
            2
        )

        # onda d'urto
        pygame.draw.circle(
            surface,
            (255, 0, 0),
            (sx, sy),
            shockwave,
            2
        )

        # fireball
        pygame.draw.circle(
            surface,
            (255, 255, 0),
            (sx, sy),
            fireball
        )

running = True

while running:

    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # click mouse -> crea esplosione
        if event.type == pygame.MOUSEBUTTONDOWN:

            # zoom con rotella
            if event.button == 4 or event.button == 5:

                mx, my = pygame.mouse.get_pos()

                # posizione nel mondo PRIMA dello zoom
                world_x = (mx - offset_x) / zoom
                world_y = (my - offset_y) / zoom

                # cambia zoom
                if event.button == 4:
                    zoom *= 1.1
                else:
                    zoom /= 1.1

                zoom = max(min_zoom, min(max_zoom, zoom))

                # mantiene il cursore fermo sul punto zoomato
                offset_x = mx - world_x * zoom
                offset_y = my - world_y * zoom

            # click sinistro
            elif event.button == 1:

                mx, my = pygame.mouse.get_pos()

                # coordinate schermo -> mondo
                world_x = (mx - offset_x) / zoom
                world_y = (my - offset_y) / zoom

                # potenza bomba
                power = 20

                explosions.append(
                    Explosion(world_x, world_y, power)
                )

    # scala mappa
    map_width = int(original_map.get_width() * zoom)
    map_height = int(original_map.get_height() * zoom)

    scaled_map = pygame.transform.smoothscale(
        original_map,
        (map_width, map_height)
    )

    # disegna mappa
    screen.fill((0, 0, 0))
    screen.blit(scaled_map, (offset_x, offset_y))

    # disegna esplosioni
    for exp in explosions:
        exp.draw(screen)

    pygame.display.flip()

pygame.quit()