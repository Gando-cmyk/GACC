import pygame
import math

pygame.init()

WIDTH = 1200
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini NukeMap")

clock = pygame.time.Clock()

# carica mappa
map_img = pygame.image.load("map.png")
map_img = pygame.transform.scale(map_img, (WIDTH, HEIGHT))

# lista esplosioni
explosions = []

class Explosion:
    def __init__(self, x, y, power):
        self.x = x
        self.y = y
        self.power = power

        # raggi
        self.fireball = power * 2
        self.shockwave = power * 5
        self.thermal = power * 8

    def draw(self, surface):

        # termico
        pygame.draw.circle(
            surface,
            (255, 120, 0),
            (self.x, self.y),
            int(self.thermal),
            2
        )

        # onda d'urto
        pygame.draw.circle(
            surface,
            (255, 0, 0),
            (self.x, self.y),
            int(self.shockwave),
            2
        )

        # fireball
        pygame.draw.circle(
            surface,
            (255, 255, 0),
            (self.x, self.y),
            int(self.fireball)
        )

running = True

while running:

    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            mx, my = pygame.mouse.get_pos()

            # potenza bomba
            power = 20

            explosions.append(
                Explosion(mx, my, power)
            )

    screen.blit(map_img, (0, 0))

    for exp in explosions:
        exp.draw(screen)

    pygame.display.flip()

pygame.quit()