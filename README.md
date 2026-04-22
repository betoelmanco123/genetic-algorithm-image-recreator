# Image Recreator

A Python project that uses a genetic algorithm to recreate a target image starting from random noise.


## Black and White Version

![Black and White Demonstration](sprites/evolution.gif)

## Color Version

![Color Demonstration](sprites/gojo.gif)

---

## How It Works

1. The program starts with a randomly generated image.
2. It creates new generations by applying random mutations.
3. Each generated image is evaluated using a fitness function.
4. The best candidate is selected.
5. This process repeats until the generated image becomes increasingly similar to the target image.

---

## RGB Color Strategy

Recreating grayscale images is relatively simple, but RGB images are more complex because each pixel contains three values:

- Red
- Green
- Blue

Instead of evolving all three values at once, the image is split into three grayscale channels.

The algorithm runs independently on each channel:

- Red channel evolution
- Green channel evolution
- Blue channel evolution

Once all channels are optimized, they are merged back together to reconstruct the final color image.

---

## Technologies Used

- Python
- NumPy
- Pygame
- Genetic Algorithms

---

## Future Improvements

- Faster mutation strategies
- Parallel processing
- Higher resolution support
- Better fitness optimization
- Real-time statistics panel

---

## Installation

```bash
git clone https://github.com/betoelmanco123/genetic-algorithm-image-recreator
cd image_recreator
pip install -r requirements.txt
python main.py
```
## Assets

"Curi of GusGus" sprite by Koren Joestar

All rights belong to the original creator.
Used with respect to the author's terms.