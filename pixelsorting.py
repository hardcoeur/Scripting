from PIL import Image
import numpy as np
import sys

class PixelSorter:
    def __init__(self):
        # Sorting modes: 0=white, 1=black, 2=bright, 3=dark
        self.mode = 0
        
        # Image path and type
        self.img_filename = "mountains"
        self.file_type = "png"
        
        # Threshold values
        self.white_value = 100 # Better balance for white sorting
        self.black_value = -1000000  # More reasonable threshold for black detection
        self.bright_value = 127
        self.dark_value = 223
        
        # State variables
        self.row = 0
        self.column = 0
        self.saved = False
        self.loops = 1
        
        # Load image
        self.img = Image.open(f"{self.img_filename}.{self.file_type}")
        self.pixels = np.array(self.img)
        self.width, self.height = self.img.size
    
    def run(self):
        for _ in range(self.loops):
            print("Sorting Columns")
            while self.column < self.width - 1:
                self.sort_column()
                self.column += 1
            
            print("Sorting Rows")
            while self.row < self.height - 1:
                self.sort_row()
                self.row += 1
        
        # Save result
        if not self.saved:
            output_img = Image.fromarray(self.pixels)
            output_img.save(f"{self.img_filename}_{self.mode}.png")
            self.saved = True
            print("Image saved")
    
    def sort_row(self):
        y = self.row
        x = 0
        x_end = 0
        
        while x_end < self.width - 1:
            if self.mode == 0:
                x = self.get_first_not_white_x(x, y)
                x_end = self.get_next_white_x(x, y)
            elif self.mode == 1:
                x = self.get_first_not_black_x(x, y)
                x_end = self.get_next_black_x(x, y)
            elif self.mode == 2:
                x = self.get_first_not_bright_x(x, y)
                x_end = self.get_next_bright_x(x, y)
            elif self.mode == 3:
                x = self.get_first_not_dark_x(x, y)
                x_end = self.get_next_dark_x(x, y)
            
            if x < 0:
                break
            
            sorting_length = x_end - x
            if sorting_length <= 0:
                x = x_end + 1
                continue
            
            # Extract and sort the pixel segment
            segment = self.pixels[y, x:x_end]
            sorted_segment = np.sort(segment, axis=0)
            self.pixels[y, x:x_end] = sorted_segment
            
            x = x_end + 1
    
    def sort_column(self):
        x = self.column
        y = 0
        y_end = 0
        
        while y_end < self.height - 1:
            if self.mode == 0:
                y = self.get_first_not_white_y(x, y)
                y_end = self.get_next_white_y(x, y)
            elif self.mode == 1:
                y = self.get_first_not_black_y(x, y)
                y_end = self.get_next_black_y(x, y)
            elif self.mode == 2:
                y = self.get_first_not_bright_y(x, y)
                y_end = self.get_next_bright_y(x, y)
            elif self.mode == 3:
                y = self.get_first_not_dark_y(x, y)
                y_end = self.get_next_dark_y(x, y)
            
            if y < 0:
                break
            
            sorting_length = y_end - y
            if sorting_length <= 0:
                y = y_end + 1
                continue
            
            # Extract and sort the pixel segment
            segment = self.pixels[y:y_end, x]
            sorted_segment = np.sort(segment, axis=0)
            self.pixels[y:y_end, x] = sorted_segment
            
            y = y_end + 1
    
    # Helper methods for x-axis (row) sorting
    def get_first_not_white_x(self, x, y):
        while self.get_pixel_value(x, y) < self.white_value:
            x += 1
            if x >= self.width:
                return -1
        return x
    
    def get_next_white_x(self, x, y):
        x += 1
        while x < self.width and self.get_pixel_value(x, y) > self.white_value:
            x += 1
        return min(x - 1, self.width - 1)
    
    def get_first_not_black_x(self, x, y):
        while self.get_pixel_value(x, y) > self.black_value:
            x += 1
            if x >= self.width:
                return -1
        return x
    
    def get_next_black_x(self, x, y):
        x += 1
        while x < self.width and self.get_pixel_value(x, y) < self.black_value:
            x += 1
        return min(x - 1, self.width - 1)
    
    def get_first_not_bright_x(self, x, y):
        while self.get_brightness(x, y) < self.bright_value:
            x += 1
            if x >= self.width:
                return -1
        return x
    
    def get_next_bright_x(self, x, y):
        x += 1
        while x < self.width and self.get_brightness(x, y) > self.bright_value:
            x += 1
        return min(x - 1, self.width - 1)
    
    def get_first_not_dark_x(self, x, y):
        while self.get_brightness(x, y) > self.dark_value:
            x += 1
            if x >= self.width:
                return -1
        return x
    
    def get_next_dark_x(self, x, y):
        x += 1
        while self.get_brightness(x, y) < self.dark_value:
            x += 1
            if x >= self.width:
                return self.width - 1
        return x - 1
    
    # Helper methods for y-axis (column) sorting
    def get_first_not_white_y(self, x, y):
        if y < self.height:
            while self.get_pixel_value(x, y) < self.white_value:
                y += 1
                if y >= self.height:
                    return -1
        return y
    
    def get_next_white_y(self, x, y):
        y += 1
        if y < self.height:
            while self.get_pixel_value(x, y) > self.white_value:
                y += 1
                if y >= self.height:
                    return self.height - 1
        return y - 1
    
    def get_first_not_black_y(self, x, y):
        if y < self.height:
            while self.get_pixel_value(x, y) > self.black_value:
                y += 1
                if y >= self.height:
                    return -1
        return y
    
    def get_next_black_y(self, x, y):
        y += 1
        if y < self.height:
            while self.get_pixel_value(x, y) < self.black_value:
                y += 1
                if y >= self.height:
                    return self.height - 1
        return y - 1
    
    def get_first_not_bright_y(self, x, y):
        if y < self.height:
            while self.get_brightness(x, y) < self.bright_value:
                y += 1
                if y >= self.height:
                    return -1
        return y
    
    def get_next_bright_y(self, x, y):
        y += 1
        if y < self.height:
            while self.get_brightness(x, y) > self.bright_value:
                y += 1
                if y >= self.height:
                    return self.height - 1
        return y - 1
    
    def get_first_not_dark_y(self, x, y):
        if y < self.height:
            while self.get_brightness(x, y) > self.dark_value:
                y += 1
                if y >= self.height:
                    return -1
        return y
    
    def get_next_dark_y(self, x, y):
        y += 1
        if y < self.height:
            while self.get_brightness(x, y) < self.dark_value:
                y += 1
                if y >= self.height:
                    return self.height - 1
        return y - 1
    
    def get_pixel_value(self, x, y):
        """Calculate absolute RGB value (r*g*b) with 32-bit overflow handling"""
        r, g, b = self.pixels[y, x][:3]
        return np.int32(r) * np.int32(g) * np.int32(b)
    
    def get_brightness(self, x, y):
        """Calculate brightness using standard formula"""
        r, g, b = self.pixels[y, x][:3]
        return 0.299 * r + 0.587 * g + 0.114 * b

if __name__ == "__main__":
    sorter = PixelSorter()
    sorter.run()