import pygame
import numpy as np
from utils import (

    random_image_block,
    new_block_generation,
    divide_and_conquer,
    fitness,
    resize,
    get_matrix_bw,
    fitness_batch


)

WIDTH = 800
HEIGH = 800


img_size = 320


class Game:

    def __init__(self):
        pygame.init()

        self.block_list = [160, 128, 80, 64, 40, 32, 20, 16, 10, 8, 5, 2, 1]
        self.screen = pygame.display.set_mode((WIDTH, HEIGH))
        self.color = pygame.Rect(0, 0, 800, 800)
        self.start_color = random_image_block(img_size, img_size, self.block_list[0])
        self.current_images = [
            random_image_block(img_size, img_size, self.block_list[0]) for _ in range(10)
        ]
        matrix = get_matrix_bw("images/image2.jpeg")
        self.matrix = np.rot90(matrix)
        self.target = resize(self.matrix, img_size)
        self.tag = 0
        self.block_size = self.block_list[self.tag]
        self.target_blocks = divide_and_conquer(self.target, number=self.block_size)
        self.counter = 0
        self.ready = False
        self.current = 100000000000000000000

    def update_image(self):

        self.surface = pygame.surfarray.make_surface(
            np.stack((self.start_color, self.start_color, self.start_color), axis=2)
        )

    def new_images(self):
        self.counter += 1

        scores = fitness_batch(self.current_images, self.target)
        idx = np.argsort(scores)
        winners = [self.current_images[i] for i in idx[:3]]
        winner = winners[-1]
        self.start_color = winner 
        fitness_current = fitness(
            self.target, winner
        )
        value = int(self.current) - int(fitness_current)

        self.current = fitness_current
        # Move to next block stage only when fitness is effectively stalled.
        if abs(value) < 5  and self.tag < len(self.block_list) - 1:
            self.tag += 1
            self.counter = 0
            self.block_size = self.block_list[self.tag]
            self.target_blocks = divide_and_conquer(self.target, number=self.block_size)


        self.current_images = list()

        for i in winners:

            self.current_images.extend(
                new_block_generation(i, self.target_blocks, size_block=self.block_size)
            )

            self.current_images.append(i)



    def run_animation(self):
        running = True
        while running:

            pygame.draw.rect(self.screen, "#001d3d", self.color)

            # horizontal
            pygame.draw.line(self.screen, (255, 255, 255), (0, 600), (600, 600))

            # vertical
            pygame.draw.line(self.screen, (255, 255, 255), (600, 0), (600, 600))

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

            self.update_image()
            self.new_images()

            self.screen.blit(self.surface, (0, 0))
            pygame.display.flip()

            pygame.display.update()


juego = Game()

juego.run_animation()
