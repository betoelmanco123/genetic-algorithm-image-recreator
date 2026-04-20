from PIL import Image
import os

carpeta = "frames"

archivos = sorted(os.listdir(carpeta))

seleccionados = []

for i, archivo in enumerate(archivos):
    
    if i < 199:
        seleccionados.append(archivo)

    elif i % 20 == 0:
        seleccionados.append(archivo)

frames = []

for archivo in seleccionados:
    ruta = os.path.join(carpeta, archivo)
    frames.append(Image.open(ruta))

frames[0].save(
    "gojo.gif",
    save_all=True,
    append_images=frames[1:],
    duration=60,
    loop=0
)