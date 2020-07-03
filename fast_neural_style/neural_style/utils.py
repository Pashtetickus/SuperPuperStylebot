from PIL import Image
import numpy 

def save_image(data):
    img = data.clone().cpu().clamp(0, 255).numpy()
    img = img.transpose(1, 2, 0).astype("uint8")
    img = Image.fromarray(img)
    return img