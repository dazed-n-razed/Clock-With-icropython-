import os
from PIL import Image, ImageOps, ImageEnhance

# Set your folder path
script_dir = os.path.dirname(os.path.abspath(__file__))

def convert_gif_high_quality(gif_name, output_txt="output_repo.txt", max_frames=20):
    gif_path = os.path.join(script_dir, gif_name)
    
    if not os.path.exists(gif_path):
        print(f"Error: {gif_path} not found.")
        return

    # target resolution - Change to 128x128 if you have a square display
    WIDTH, HEIGHT = 128, 64 

    img = Image.open(gif_path)
    
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("gif_frames = [\n")
        
        for frame_index in range(min(img.n_frames, max_frames)):
            img.seek(frame_index)
            
            # 1. Convert to RGB first for processing
            frame = img.convert('RGB')
            
            # 2. Upscale/Resize using LANCZOS (Highest Quality scaling)
            frame = frame.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
            
            # 3. ENHANCE: Boost Contrast and Sharpness
            # This makes the 1-bit conversion look much cleaner
            frame = ImageEnhance.Contrast(frame).enhance(1.5) 
            frame = ImageEnhance.Sharpness(frame).enhance(2.0)
            
            # 4. Convert to 1-bit Monochrome
            # We use Floyd-Steinberg dithering to simulate "shades"
            frame = frame.convert('1', dither=Image.Dither.FLOYDSTEINBERG)
            
            # 5. Get bytes and write
            data = frame.tobytes()
            f.write(f"    bytearray({repr(data)}),  # Frame {frame_index}\n")
            
        f.write("]\n")
        
    print(f"Success! High-quality frames saved to {output_txt}")

# RUN IT
convert_gif_high_quality("asd.gif")