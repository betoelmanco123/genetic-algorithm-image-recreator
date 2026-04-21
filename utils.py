from PIL import Image
import numpy as np
import random
import math

def square_sizes(img_size, min_size=1, reverse=True):
    m, n = img_size
    g = math.gcd(m, n)

    sizes = [k for k in range(min_size, g + 1) if g % k == 0]

    return sorted(sizes, reverse=reverse)



def get_matrix_bw(imgname, img_size):
    image = Image.open(imgname).convert("L")
    image = image.resize((img_size, img_size))

    arr = np.array(image)
    return arr.T

def get_matrix(imgname, img_size):
    """
    imgname: the name of the image
    img_size: this funcition resize the original image, give the desired new size
    """
    
    h, w = (img_size)
    
    image = Image.open(imgname)
    image = image.resize((w, h))

    arr = np.array(image)
    if arr.ndim == 2:
        return arr.T

    return np.transpose(arr, (1, 0, 2))


def fitness(target, current):
    diff = target.astype(np.int16) - current.astype(np.int16)
    return np.abs(diff).sum()


def all_blocks_fitness(target_blocks, current_blocks):
    diff = target_blocks.astype(np.int16) - current_blocks.astype(np.int16)
    return np.abs(diff).sum(axis=(2, 3))


def block_fitness(current, target, size_block, block_position):
    """
    Compara un bloque puntual entre current y target y retorna su fitness.

    Parámetros:
        current        -> imagen actual 2D
        target         -> imagen objetivo 2D
        size_block     -> tamaño del bloque en pixeles
        block_position -> (row_block, col_block)

    Retorna:
        Suma absoluta de diferencias del bloque (menor es mejor)
    """

    if current.shape != target.shape:
        raise ValueError("current y target deben tener la misma forma")

    if len(block_position) != 2:
        raise ValueError("block_position debe tener formato (row, col)")

    row_block, col_block = block_position
    y1 = int(row_block) * size_block
    x1 = int(col_block) * size_block
    y2 = y1 + size_block
    x2 = x1 + size_block

    h, w = current.shape
    if y1 < 0 or x1 < 0 or y2 > h or x2 > w:
        raise IndexError("block_position fuera de rango para size_block")

    current_block = current[y1:y2, x1:x2].astype(np.int16)
    target_block = target[y1:y2, x1:x2].astype(np.int16)

    return np.abs(target_block - current_block).sum()


def best_image_from_generation(target_blocks, size_block, generation, num_worst=15):
    """
    Toma una generación de imágenes y construye una sola imagen final:
    - identifica bloques peores con get_worst
    - elige el mejor bloque por posición usando block_fitness
    - conserva bloques no modificados de la imagen base
    """

    if not generation:
        raise ValueError("generation no puede estar vacía")

    base_image = generation[0]
    base_blocks = divide_and_conquer(base_image, number=size_block)
    target_image = rebuild_from_blocks(target_blocks)

    worst_coords = get_worst(base_blocks, target_blocks, num=num_worst)

    result_blocks = base_blocks.copy()

    for y, x in worst_coords:
        best_score = float("inf")
        best_idx = 0

        for idx, candidate in enumerate(generation):
            score = block_fitness(
                candidate,
                target_image,
                size_block=size_block,
                block_position=(int(y), int(x)),
            )
            if score < best_score:
                best_score = score
                best_idx = idx

        candidate_blocks = divide_and_conquer(generation[best_idx], number=size_block)
        result_blocks[int(y), int(x)] = candidate_blocks[int(y), int(x)]

    return rebuild_from_blocks(result_blocks)


def mutate_array(arr, rate=0.1):
    out = arr.copy().astype(np.int16)
    mask = np.random.random(arr.shape) < rate
    noise = np.random.randint(-10, 10, arr.shape)
    out[mask] += noise[mask]
    return np.clip(out, 0, 255).astype(np.uint8)


def new_generation(arr):

    gene = list()

    for _ in range(20):
        temp = mutate_array(arr)
        gene.append(temp)

    return gene


def divide_and_conquer(arr, number=10):
    # `number` is the block size in pixels (kept for backward compatibility).
    block_size = number
    h, w = arr.shape

    # Validar que sea divisible exactamente
    if h % block_size != 0 or w % block_size != 0:
        raise ValueError("Las dimensiones deben ser divisibles por block_size")

    # Reorganizar en bloques
    blocks = arr.reshape(h // block_size, block_size, w // block_size, block_size)

    # Reordenar ejes para obtener matriz de bloques
    blocks = blocks.swapaxes(1, 2)

    return blocks


def get_worst(arr, target, num=15):

    scores = all_blocks_fitness(arr, target)

    # Si un bloque ya coincide exactamente con el objetivo, no se vuelve a considerar.
    scores = np.where(scores == 0, -1, scores)

    valid_flat = np.flatnonzero(scores.ravel() > 0)
    if valid_flat.size == 0:
        return np.empty((0, 2), dtype=int)

    flat_scores = scores.ravel()[valid_flat]
    order = np.argsort(flat_scores)[::-1][:num]
    flat_sorted = valid_flat[order]
    coords = np.array(np.unravel_index(flat_sorted, scores.shape)).T

    return coords


def mutate_blocks(blocks, coords, intensity=10):

    new_blocks = blocks.copy()

    for i, j in coords:
        noise = np.random.randint(
            -intensity, intensity + 1, size=new_blocks[i, j].shape
        )

        mutated = new_blocks[i, j].astype(np.int16) + noise
        new_blocks[i, j] = np.clip(mutated, 0, 255)

    return new_blocks


def rebuild_from_blocks(blocks):
    bh, bw = blocks.shape[:2]  # cantidad de bloques
    block_h, block_w = blocks.shape[2:4]

    return blocks.swapaxes(1, 2).reshape(bh * block_h, bw * block_w, *blocks.shape[4:])


def new_block_generation(arr, target, size_block):

    new = divide_and_conquer(arr, number=size_block)

    worst = get_worst(new, target, num=80)
    temp = list()

    for i in range(40):
        child = mutate_one_color(new, worst)
        temp.append(rebuild_from_blocks(child))

    return temp


def new_none_block(arr, target, size_block):
    new = divide_and_conquer(arr, number=size_block)

    worst = get_worst(new, target)
    temp = list()

    for i in range(20):
        child = mutate_blocks(new, worst)
        temp.append(rebuild_from_blocks(child))

    return temp


def get_winners(population, target, n=5):
    scored = []

    for individual in population:
        score = fitness(target, individual)
        scored.append((score, individual))

    scored.sort(key=lambda x: x[0])  # menor fitness primero

    return [ind for score, ind in scored[:n]]


def random_image(width, heigh):
    img = np.array(
        [[random.randint(0, 255) for _ in range(width)] for _ in range(heigh)]
    )
    return img


def random_image_block(width, height, size):
    """
    Crea una imagen en blanco y negro por bloques.
    Cada bloque tiene un solo valor aleatorio entre 1 y 255.
    Size, el tamaño de los bloques en que se dividira
    """

    img = np.zeros((height, width), dtype=np.uint8)

    for y in range(0, height, size):
        for x in range(0, width, size):

            # Gris aleatorio
            color = np.random.randint(0, 256, dtype=np.uint8)

            y_end = min(y + size, height)
            x_end = min(x + size, width)

            img[y:y_end, x:x_end] = color

    return img


def fitness_batch(population, target):
    pop = np.array(population, dtype=np.int16)
    tar = target.astype(np.int16)

    return np.abs(pop - tar).sum(axis=(1, 2))


def mutate_one_color(arr, coords, amount=50):
    """
    Mutar bloques específicos ajustando su color actual.
    No modifica el original.

    Parámetros:
        arr     -> np.ndarray dividido en bloques
                   ejemplo: (160, 160, 10, 10)
        coords  -> [(y, x), ...]
        amount  -> máximo cambio (+/-)

    Retorna:
        Copia mutada
    """

    mutated = arr.copy()

    for y, x in coords:
        # Tomamos el color actual del bloque
        current = int(mutated[y, x, 0, 0])

        # Cambio pequeño para afinar
        delta = np.random.randint(-amount, amount + 1)

        new_color = np.clip(current + delta, 0, 255)

        # Aplicar mismo color a todo el bloque
        mutated[y, x] = new_color

    return mutated


def resize(img, size):
    small = Image.fromarray(img).resize((size, size))
    small = np.array(small)
    return small


def main():
    print("Hello from image_recreator!")


if __name__ == "__main__":
    main()
