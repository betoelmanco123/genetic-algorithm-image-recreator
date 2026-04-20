import numpy as np
from utils import (
    random_image_block,
    new_block_generation,
    best_image_from_generation,
    divide_and_conquer,
    fitness,
    resize,
    get_matrix,
    fitness_batch,
    square_sizes,
)


class image_evolution:
    
    def __init__(self, target, img_size):
        self.block_list = square_sizes(img_size)
        self.block_size = self.block_list[0]
        self.current_images = [random_image_block(img_size[0], img_size[1], self.block_list[0]) for _ in range(20)]
        
        self.start_color = self.current_images[0]
        self.generation = 0
        self.target = target
        self.target_blocks = divide_and_conquer(target, self.block_size)
        self.tag = 0
        self.current = 1000000000000000
        
    
    
    def new_images(self):
        self.generation += 1


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