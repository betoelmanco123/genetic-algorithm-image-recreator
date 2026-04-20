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
    get_matrix_bw,
    get_matrix,
    fitness_batch,
)
from super_image import image_evolution

IMG_NAME = "images/image8.jpg"

WIDTH = 1310
HEIGH = 800


img_size_w = 320
img_size_h = 580

img_size = (img_size_w, img_size_h)

class Game:

    def __init__(self):
        pygame.init()
        # Crear carpeta frames si no existe
        os.makedirs("frames", exist_ok=True)
        
        self.graphic_size = 600
    
        self.screen = pygame.display.set_mode((WIDTH, HEIGH))
        self.color = pygame.Rect(0, 0, 1310, 800)
        
        
        target_matrix = get_matrix(IMG_NAME, img_size)
        target_matrix = np.rot90(target_matrix)
        red_matrix = target_matrix[:, :, 0]
        green_matrix = target_matrix[:, :, 1]
        blue_matrix = target_matrix[:, :, 2]
        
        
        self.red_image = image_evolution(red_matrix, img_size)
        self.green_image = image_evolution(green_matrix, img_size)
        self.blue_image = image_evolution(blue_matrix, img_size)

        self.current = 100000000000000


        
        self.font = pygame.font.SysFont(None, 48)
        self.generation = 0
        self.values = [None] * self.graphic_size
        self.value = 0
        
        self.zeros = np.zeros_like(self.blue_image.start_color)

    def update_images(self):

        self.surface_red = pygame.surfarray.make_surface(
            np.stack((self.red_image.start_color, self.zeros, self.zeros), axis=2)
        )
        self.surface_green = pygame.surfarray.make_surface(
            np.stack((self.zeros, self.green_image.start_color,self.zeros), axis=2)
        )
        self.surface_blue = pygame.surfarray.make_surface(
            np.stack((self.zeros, self.zeros, self.blue_image.start_color), axis=2)
        )
        
        self.surface_total = pygame.surfarray.make_surface(
            np.stack((self.red_image.start_color, self.green_image.start_color, self.blue_image.start_color), axis=2)
        )



    def run_graphic(self):

        self.values.pop(0)
        self.values.append(self.value / 100)

        for x in range(10, self.graphic_size - 1):

            if self.values[x] is None:
                continue

            y1 = max(680, 760 - self.values[x])
            y2 = max(680, 760 - self.values[x + 1])

            pygame.draw.line(self.screen, "#ffc300", (x, y1), (x + 1, y2), 2)
            pygame.draw.line(self.screen, "#ffffff", (10, 760), (self.graphic_size, 760), 2)
            
        y_end = max(680, 760 - self.values[self.graphic_size - 1])
        pygame.draw.circle(self.screen, "#ffc300", (self.graphic_size, y_end), 5)
        
    def update_data(self):
        
        self.current = self.red_image.current + self.green_image.current + self.red_image.current
        self.value = (self.current) // 4000
    def run_animation(self):
        running = True
        while running:

            pygame.draw.rect(self.screen, "#001d3d", self.color)

            # horizontal
            pygame.draw.line(self.screen, (255, 255, 255), (10, 670), (1300, 670), width=2)

            self.run_graphic()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

            pygame.display.set_caption("Img recreator")

            texto = self.font.render(f"Fitness: {self.current} ", True, (255, 255, 255))
            text = self.font.render(
                f"Generation: {self.generation}", True, (255, 255, 255)
            )
            self.screen.blit(texto, (670, 730))
            self.screen.blit(text, (990, 730))

            self.update_images()
            self.red_image.new_images()
            self.green_image.new_images()
            self.blue_image.new_images()
            self.update_data()

            self.screen.blit(self.surface_red, (10, 10))
            self.screen.blit(self.surface_green, (10, 340))
            self.screen.blit(self.surface_blue, (645, 10))
            self.screen.blit(self.surface_total, (645, 340))
            
            self.generation += 1

            pygame.display.flip()

            pygame.display.update()
            
            pygame.image.save(self.screen, f"frames/frame_{self.generation:04d}.png")



juego = Game()

juego.run_animation()
