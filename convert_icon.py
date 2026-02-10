from PIL import Image
import os

png_path = 'following.png'
ico_path = 'following.ico'

if os.path.exists(png_path):
    img = Image.open(png_path)
    img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]) # Better multi-size icon
    print(f"Successfully converted {png_path} to {ico_path}")
else:
    print(f"Error: {png_path} not found")
