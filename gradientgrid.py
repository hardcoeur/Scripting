import pygame
import random
import os
import sys
from PIL import Image

# Configuration
image_name = "pewpew"
gradient_type = 0  # 0 for linear, 1 for radial
edge_smoothing = True
random_shape_freq = True
shape_freq = 75
i_shape_freq = shape_freq
image_scale = 1

# Initialize pygame
pygame.init()
print("Initialized pygame")

def clamp(value, min_val=0, max_val=255):
    return max(min_val, min(value, max_val))

def to_color(color, alpha=255):
    if isinstance(color, pygame.Color):
        return color
    if len(color) == 3:
        return pygame.Color(clamp(color[0]), clamp(color[1]), clamp(color[2]), alpha)
    return pygame.Color(clamp(color[0]), clamp(color[1]), clamp(color[2]), clamp(color[3]))

def brightness(color):
    color = to_color(color)
    return 0.299 * color.r + 0.587 * color.g + 0.114 * color.b

class Gradient:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.size = w * h  # Track shape size for shadow selection
    
    def get_color1(self, x, y):
        if 0 <= x < screen_width and 0 <= y < screen_height:
            return to_color(img.get_at((x, y)))
        return pygame.Color(0, 0, 0)
    
    def get_color2(self, x, y):
        if 0 <= x < screen_width and 0 <= y < screen_height:
            return to_color(img.get_at((x, y)))
        return pygame.Color(0, 0, 0)
    
    def draw_shadow(self, color):
        """Draw 1px dropshadow with 20% opacity"""
        shadow_color = to_color(color, 51)  # 20% of 255
        if gradient_type == 0:  # Linear gradient shadow
            pygame.draw.line(screen, shadow_color, 
                           (self.x+1, self.y+self.h+1), 
                           (self.x+self.w+1, self.y+self.h+1), 1)
        else:  # Radial gradient shadow
            pygame.draw.circle(screen, shadow_color, 
                             (self.x+1, self.y+1), self.w)
    
    def draw_linear_gradient(self, c1, c2):
        c1 = to_color(c1)
        c2 = to_color(c2)
        for i in range(self.x, min(self.x + self.w, screen_width)):
            inter = (i - self.x) / self.w
            r = random.uniform(0, 8)
            new_r = clamp(int(c1.r + (c2.r - c1.r) * inter * r))
            new_g = clamp(int(c1.g + (c2.g - c1.g) * inter * r))
            new_b = clamp(int(c1.b + (c2.b - c1.b) * inter * r))
            color = pygame.Color(new_r, new_g, new_b)
            pygame.draw.line(screen, color, (i, self.y), (i, min(self.y + self.h, screen_height)))
    
    def draw_radial_gradient(self, c1, c2):
        c1 = to_color(c1)
        c2 = to_color(c2)
        for i in range(self.w, 0, -1):
            inter = i / self.w
            r = random.uniform(0.1, 2)
            new_r = clamp(int(c1.r + (c2.r - c1.r) * inter * r))
            new_g = clamp(int(c1.g + (c2.g - c1.g) * inter * r))
            new_b = clamp(int(c1.b + (c2.b - c1.b) * inter * r))
            color = pygame.Color(new_r, new_g, new_b)
            pygame.draw.circle(screen, color, (self.x, self.y), i)

def main():
    global screen, screen_width, screen_height, img, shape_freq
    
    print(f"Loading image: {image_name}.png")
    try:
        pil_img = Image.open(image_name + ".png")
        img_width, img_height = pil_img.size
        screen_width, screen_height = img_width * image_scale, img_height * image_scale
        print(f"Screen size: {screen_width}x{screen_height}")
        screen = pygame.display.set_mode((screen_width, screen_height))
        
        img = pygame.image.fromstring(pil_img.tobytes(), pil_img.size, pil_img.mode)
        img = pygame.transform.scale(img, (screen_width, screen_height))
    except Exception as e:
        print(f"Error loading image: {str(e)}")
        sys.exit(1)

    os.makedirs("done", exist_ok=True)
    screen.fill(to_color(img.get_at((1, 1))))
    pygame.display.flip()

    # Generate all gradients first to determine largest shapes
    gradients = []
    for x in range(0, screen_width + 1, max(1, screen_width // shape_freq)):
        for y in range(0, screen_height + 1, max(1, screen_height // shape_freq)):
            w = max(1, screen_width // shape_freq * 2)
            h = max(1, screen_height // shape_freq * 2)
            gradients.append(Gradient(x, y, w, h))
            if random_shape_freq:
                shape_freq = int(random.uniform(25, i_shape_freq))

    # Find largest 10% of shapes for shadows
    gradients.sort(key=lambda g: g.size, reverse=True)
    large_shapes = gradients[:len(gradients)//10]

    print(f"Drawing {len(gradients)} gradients with shadows on {len(large_shapes)} largest")
    
    # Draw shadows first
    for shape in large_shapes:
        c1 = shape.get_color1(shape.x, shape.y)
        shape.draw_shadow(c1)

    # Then draw all gradients
    for shape in gradients:
        c1 = shape.get_color1(shape.x, shape.y)
        c2 = shape.get_color2(shape.x + shape.w, shape.y + shape.h)
        
        if gradient_type == 0:
            if edge_smoothing and brightness(c1) - brightness(c2) > 10:
                shape.draw_linear_gradient(shape.get_color2(shape.x - shape.w//10, shape.y - shape.h), c1)
            else:
                shape.draw_linear_gradient(c1, c2)
        else:
            if edge_smoothing and brightness(c1) - brightness(c2) > 10:
                shape.draw_radial_gradient(shape.get_color2(shape.x - shape.w//20, shape.y - shape.h), c1)
            else:
                shape.draw_radial_gradient(c1, c2)

    pygame.display.flip()
    output_path = f"done/{image_name}_with_shadow.png"
    pygame.image.save(screen, output_path)
    print(f"Saved to {output_path}")
    pygame.quit()

if __name__ == "__main__":
    main()