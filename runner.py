import pygame
import numpy as np
import os
from utils import (
    random_image_block,
    new_block_generation,
    best_image_from_generation,
    divide_and_conquer,
    fitness,
    resize,
    get_matrix,
    fitness_batch,
)

IMG_NAME = "images/image6.jpeg"

WIDTH = 1310
HEIGH = 800


img_size = 640


class Game:

    def __init__(self):
        pygame.init()
        # Crear carpeta frames si no existe
        os.makedirs("frames", exist_ok=True)
        
        self.graphic_size = 600
        self.block_list = [160, 80, 64, 40, 32, 20, 16, 10, 8, 5, 2, 1]
        self.screen = pygame.display.set_mode((WIDTH, HEIGH))
        self.color = pygame.Rect(0, 0, 1310, 800)
        self.start_color = random_image_block(img_size, img_size, self.block_list[0])
        self.current_images = [
            random_image_block(img_size, img_size, self.block_list[0])
            for _ in range(10)
        ]
        matrix = get_matrix(IMG_NAME, img_size)
        self.matrix = np.rot90(matrix)

        self.target = resize(self.matrix, img_size)
        self.tag = 0
        self.block_size = self.block_list[self.tag]
        self.target_blocks = divide_and_conquer(self.target, number=self.block_size)
        self.counter = 0
        self.ready = False
        self.current = 100000000000000

        self.visual_target = pygame.image.load(IMG_NAME)
        self.visual_target = pygame.transform.scale(
            self.visual_target, (img_size, img_size)
        )
        self.font = pygame.font.SysFont(None, 48)
        self.generation = 0
        self.values = [None] * self.graphic_size
        self.value = 0

    def update_image(self):

        self.surface = pygame.surfarray.make_surface(
            np.stack((self.start_color, self.start_color, self.start_color), axis=2)
        )

    def new_images(self):
        self.generation += 1
        self.counter += 1

        scores = fitness_batch(self.current_images, self.target)
        idx = np.argsort(scores)
        winners = [self.current_images[i] for i in idx[:3]]
        winner = winners[0]
        self.start_color = winner
        fitness_current = fitness(self.target, winner)
        value = int(self.current) - int(fitness_current)

        self.value = value

        self.current = fitness_current
        # Move to next block stage only when fitness is effectively stalled.
        if abs(value) < 1 and self.tag < len(self.block_list) - 1:
            self.tag += 1
            self.counter = 0
            self.block_size = self.block_list[self.tag]
            self.target_blocks = divide_and_conquer(self.target, number=self.block_size)

        self.current_images = list()

        for i in winners:
            generation = new_block_generation(
                i, self.target_blocks, size_block=self.block_size
            )
            merged = best_image_from_generation(
                self.target_blocks,
                size_block=self.block_size,
                generation=generation,
                num_worst=40,
            )

            self.current_images.extend(generation)
            self.current_images.append(merged)

            self.current_images.append(i)

    def run_graphic(self):

        self.values.pop(0)
        self.values.append(self.value / 100)

        for x in range(10, self.graphic_size - 1):

            if self.values[x] is None:
                continue

            y1 = max(670, 750 - self.values[x])
            y2 = max(670, 750 - self.values[x + 1])

            pygame.draw.line(self.screen, "#ffc300", (x, y1), (x + 1, y2), 2)
            pygame.draw.line(self.screen, "#ffc300", (10, 750), (self.graphic_size, 750), 2)
            
        y_end = max(670, 750 - self.values[self.graphic_size - 1])
        pygame.draw.circle(self.screen, "#ffc300", (self.graphic_size, y_end), 5)

    def run_animation(self):
        running = True
        while running:

            pygame.draw.rect(self.screen, "#001d3d", self.color)

            # horizontal
            pygame.draw.line(self.screen, (255, 255, 255), (10, 660), (1300, 660))

            self.run_graphic()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

            pygame.display.set_caption("Img recreator")

            texto = self.font.render(f"Fitness: {self.current} ", True, (255, 255, 255))
            text = self.font.render(
                f"Generation: {self.generation}", True, (255, 255, 255)
            )
            self.screen.blit(texto, (700, 705))
            self.screen.blit(text, (1000, 705))

            self.update_image()
            self.new_images()

            self.screen.blit(self.surface, (10, 10))
            self.screen.blit(self.visual_target, (660, 10))
            pygame.display.flip()

            pygame.display.update()
            
            pygame.image.save(self.screen, f"frames/frame_{self.generation:04d}.png")



juego = Game()

juego.run_animation()
