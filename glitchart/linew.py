from PIL import Image, ImageDraw
import random
import math
import numpy as np
import os
import argparse

def hex_to_rgb(hex_color):
    """Convert hex color code to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Default settings
DEFAULT_SETTINGS = {
    'IMAGE_NAME': "pewpew.png",
    'LINE_FREQ': 60,
    'LINE_ANGLE': 90,
    'LINE_LENGTH': 60,
    'LINE_COLOR': None,  # Will be set from image by default
    'BACKGROUND_COLOR': "#000000",  # Black by default
    'SAVE_FRAMES': True,
    'FRAMES': 1,
    'SHAPE_TYPE': 0,
    'ANIMATED_INPUT': False,
    'INPUT_FRAMES': 0
}

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--line-color', help='Line color in hex (e.g. #FF0000)')
    parser.add_argument('--bg-color', help='Background color in hex (e.g. #FFFFFF)')
    return parser.parse_args()

def calculate_brightness(pixel):
    return 0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]

def quantize(value, step):
    return step * math.floor((value / step) + 0.5)

def get_weight(image, x, y, line_freq, width):
    if 0 <= x < image.width and 0 <= y < image.height:
        pixel = image.getpixel((x, y))
        brightness = calculate_brightness(pixel)
        quantized = quantize(brightness, 17)
        return int(np.interp(quantized, [0, 255], [0, width / (line_freq * 2)]))
    return 0

class Shape:
    def __init__(self, x, y, weight, color):
        self.x = x
        self.y = y
        self.weight = weight
        self.color = color
        self.l = DEFAULT_SETTINGS['LINE_LENGTH']

    def draw_rect(self, draw, angle):
        angle_rad = math.radians(angle)
        half_l = self.l / 2
        half_w = self.weight / 2
        
        points = [
            (self.x + half_l * math.cos(angle_rad) - half_w * math.sin(angle_rad),
             self.y + half_l * math.sin(angle_rad) + half_w * math.cos(angle_rad)),
            (self.x - half_l * math.cos(angle_rad) - half_w * math.sin(angle_rad),
             self.y - half_l * math.sin(angle_rad) + half_w * math.cos(angle_rad)),
            (self.x - half_l * math.cos(angle_rad) + half_w * math.sin(angle_rad),
             self.y - half_l * math.sin(angle_rad) - half_w * math.cos(angle_rad)),
            (self.x + half_l * math.cos(angle_rad) + half_w * math.sin(angle_rad),
             self.y + half_l * math.sin(angle_rad) - half_w * math.cos(angle_rad))
        ]
        
        if all(0 <= p[0] < draw.im.size[0] and 0 <= p[1] < draw.im.size[1] for p in points):
            draw.polygon(points, fill=self.color)

def main():
    args = parse_args()
    
    # Apply color settings from arguments
    settings = DEFAULT_SETTINGS.copy()
    if args.line_color:
        settings['LINE_COLOR'] = hex_to_rgb(args.line_color)
    if args.bg_color:
        settings['BACKGROUND_COLOR'] = hex_to_rgb(args.bg_color) + (0,)  # Add alpha channel
    
    image = Image.open(settings['IMAGE_NAME']).convert('RGB')
    width, height = image.size
    print(f"Image dimensions: {width}x{height}px")
    print(f"Line spacing: {width/settings['LINE_FREQ']:.1f}px | Line length: {settings['LINE_LENGTH']}px")
    
    output = Image.new('RGBA', (width, height), settings['BACKGROUND_COLOR'])
    draw = ImageDraw.Draw(output)
    
    lines = []
    for x in range(0, width, int(width / settings['LINE_FREQ'])):
        for y in range(0, height, int(height / settings['LINE_FREQ'])):
            weight = get_weight(image, x, y, settings['LINE_FREQ'], width)
            color = settings['LINE_COLOR'] or image.getpixel((x, y))
            lines.append(Shape(x, y, weight, color))
    
    for line in lines:
        line.draw_rect(draw, settings['LINE_ANGLE'])
    
    os.makedirs("done", exist_ok=True)
    output.save(os.path.join("done", settings['IMAGE_NAME']))
    print(f"Output saved to done/{settings['IMAGE_NAME']}")

if __name__ == "__main__":
    main()