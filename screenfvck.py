#!/usr/bin/env python3
import random
import time
import sys
from datetime import datetime
import os
from Xlib import display, X
from PIL import Image

class ScreenFuck:
    def __init__(self):
        """Initialize screen capture and set up buffers"""
        print("Initializing screen capture...")
        try:
            self.disp = display.Display()
            self.screen = self.disp.screen()
            self.root = self.screen.root
            
            # Get screen dimensions
            self.width = self.screen.width_in_pixels
            self.height = self.screen.height_in_pixels
            self.depth = self.screen.root_depth
            
            print(f"Screen size: {self.width}x{self.height} (depth: {self.depth})")
            
            # Calculate byte width (4 bytes per pixel)
            self.byte_width = self.width * 4
            self.byte_width = (self.byte_width + 3) & ~3  # Align to 4 bytes
            
            # Create buffer for screen data
            self.data = bytearray(self.byte_width * self.height)
            print("Initialization complete")
        except Exception as e:
            print(f"Initialization failed: {str(e)}")
            sys.exit(1)
    
    def capture_screen(self):
        """Capture the screen contents using Xlib"""
        print("Capturing screen...")
        try:
            raw = self.root.get_image(0, 0, self.width, self.height, X.ZPixmap, 0xffffffff)
            self.data = bytearray(raw.data)
            print("Screen capture successful")
        except Exception as e:
            print(f"Screen capture failed: {str(e)}")
            sys.exit(1)
    
    def manipulate_buffer(self, safe_mode=False):
        """Apply glitch effects to the buffer"""
        print("Applying glitch effects...")
        loops = random.randint(1, 200)
        
        for i in range(loops):
            try:
                if random.random() < 0.75:
                    # Apply full or partial screen glitch
                    x = random.randint(0, self.width - 1)
                    y = random.randint(0, self.height - 1)
                    
                    if random.random() < 0.1:
                        width = random.randint(1, self.width - x)
                    else:
                        width = self.width
                    
                    if random.random() < 0.1:
                        height = random.randint(1, self.height - y)
                    else:
                        height = self.height
                    
                    self._apply_glitch(x, y, width, height, safe_mode)
                else:
                    # Apply more complex glitch with sub-region
                    x = random.randint(0, self.width - 1)
                    y = random.randint(0, self.height - 1)
                    width = random.randint(1, self.width - x)
                    height = random.randint(1, self.height - y)
                    
                    self._apply_complex_glitch(x, y, width, height, safe_mode)
                
                # Show progress
                if i % 10 == 0:
                    print(f"Progress: {i+1}/{loops} glitches applied")
            except Exception as e:
                print(f"Error applying glitch: {str(e)}")
                continue
        
        print("Glitch effects complete")
    
    def _apply_glitch(self, x, y, width, height, safe_mode):
        """Apply a simple glitch effect to a region"""
        modes = 10 if not safe_mode else 8
        mode = random.randint(0, modes - 1)
        
        for row in range(y, min(y + height, self.height)):
            offset = row * self.byte_width + x * 4
            end = min(offset + width * 4, len(self.data))
            
            if mode == 0:
                # Swap color channels (only if we have enough bytes)
                for i in range(offset, end - 2, 4):
                    self.data[i], self.data[i+1], self.data[i+2] = \
                        self.data[i+2], self.data[i], self.data[i+1]
            elif mode == 1:
                # Invert colors
                for i in range(offset, end - 2, 4):
                    self.data[i] = 255 - self.data[i]
                    self.data[i+1] = 255 - self.data[i+1]
                    self.data[i+2] = 255 - self.data[i+2]
            # Additional glitch modes...
    
    def save_image(self):
        """Save the glitched image to a file"""
        print("Saving image...")
        try:
            # Convert to PIL Image
            img = Image.frombytes('RGB', (self.width, self.height), bytes(self.data))
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f"ScreenFvcked_{timestamp}.png"
            
            # Save to user's home directory
            home = os.path.expanduser('~')
            filepath = os.path.join(home, filename)
            img.save(filepath)
            print(f"Image saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"Failed to save image: {str(e)}")
            sys.exit(1)
    
    def run(self, safe_mode=False):
        """Main execution method"""
        try:
            self.capture_screen()
            self.manipulate_buffer(safe_mode)
            saved_path = self.save_image()
            return saved_path
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            sys.exit(0)

if __name__ == "__main__":
    print("Starting ScreenFvck (Python version)")
    sf = ScreenFuck()
    saved_path = sf.run()
    print(f"Glitched screenshot successfully saved to: {saved_path}")
