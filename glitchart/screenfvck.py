#!/usr/bin/env python3
import random
import time
import sys
from datetime import datetime
import os
from Xlib import display, X
from PIL import Image
import numpy as np
import ctypes
import struct
import argparse

class ScreenFuck:
    # Define glitch method names for reference
    SIMPLE_GLITCH_METHODS = [
        "swap-channels",       # 0
        "invert-colors",       # 1
        "channel-shift",       # 2
        "channel-separation",  # 3
        "pixel-sorting",       # 4
        "random-noise",        # 5
        "channel-wrap",        # 6
        "extreme-contrast",    # 7
        "color-reduction",     # 8
        "channel-zeroing"      # 9
    ]
    
    COMPLEX_GLITCH_METHODS = [
        "pixel-sort-effect",   # 0
        "data-bending",        # 1
        "noise-injection",     # 2
        "channel-manipulation", # 3
        "block-transfer",      # 4
        "scanline-effect"      # 5
    ]
    
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
            
            # Initialize enabled glitch methods
            self.enabled_simple_glitches = set(range(len(self.SIMPLE_GLITCH_METHODS)))
            self.enabled_complex_glitches = set(range(len(self.COMPLEX_GLITCH_METHODS)))
            
        except Exception as e:
            print(f"Initialization failed: {str(e)}")
            sys.exit(1)
    
    def set_enabled_glitches(self, enabled_methods=None, disabled_methods=None):
        """Set which glitch methods are enabled or disabled"""
        if enabled_methods:
            # If specific methods are enabled, start with empty set and add only those
            self.enabled_simple_glitches = set()
            self.enabled_complex_glitches = set()
            
            for method in enabled_methods:
                # Normalize method name (replace underscores with dashes)
                method = method.replace('_', '-')
                
                if method in self.SIMPLE_GLITCH_METHODS:
                    self.enabled_simple_glitches.add(self.SIMPLE_GLITCH_METHODS.index(method))
                elif method in self.COMPLEX_GLITCH_METHODS:
                    self.enabled_complex_glitches.add(self.COMPLEX_GLITCH_METHODS.index(method))
        
        if disabled_methods:
            # Remove specific methods from enabled sets
            for method in disabled_methods:
                # Normalize method name (replace underscores with dashes)
                method = method.replace('_', '-')
                
                if method in self.SIMPLE_GLITCH_METHODS:
                    idx = self.SIMPLE_GLITCH_METHODS.index(method)
                    if idx in self.enabled_simple_glitches:
                        self.enabled_simple_glitches.remove(idx)
                elif method in self.COMPLEX_GLITCH_METHODS:
                    idx = self.COMPLEX_GLITCH_METHODS.index(method)
                    if idx in self.enabled_complex_glitches:
                        self.enabled_complex_glitches.remove(idx)
        
        # Print enabled methods
        print("Enabled simple glitch methods:")
        for idx in self.enabled_simple_glitches:
            print(f"  - {self.SIMPLE_GLITCH_METHODS[idx]}")
        
        print("Enabled complex glitch methods:")
        for idx in self.enabled_complex_glitches:
            print(f"  - {self.COMPLEX_GLITCH_METHODS[idx]}")
    
    def capture_screen(self, safe_mode=False):
        """Capture the screen contents using optimized Xlib"""
        print("Capturing screen...")
        try:
            # Use optimized capture with different pixel formats
            modes = 8 if safe_mode else 10
            mode = random.randint(0, modes - 1)
            
            # Get raw data from X server
            raw = self.root.get_image(0, 0, self.width, self.height, X.ZPixmap, 0xffffffff)
            raw_data = bytearray(raw.data)
            
            # Convert based on selected mode
            if mode == 0:
                # BGRA to RGBA (default)
                self.data = raw_data
            elif mode == 1:
                # BGRA to ARGB
                self._convert_bgra_to_argb(raw_data)
            elif mode == 2:
                # 16-bit 5-5-5-1
                self._convert_to_5551(raw_data)
            elif mode == 3:
                # 16-bit 1-5-5-5 reversed
                self._convert_to_1555_rev(raw_data)
            elif mode == 4:
                # 32-bit 8-8-8-8
                self._convert_to_8888(raw_data)
            elif mode == 5:
                # 32-bit 8-8-8-8 reversed
                self._convert_to_8888_rev(raw_data)
            elif mode == 6:
                # 32-bit 10-10-10-2
                self._convert_to_1010102(raw_data)
            elif mode == 7:
                # 32-bit 2-10-10-10 reversed
                self._convert_to_2101010_rev(raw_data)
            elif mode == 8:
                # 16-bit unsigned short
                self._convert_to_ushort(raw_data)
            elif mode == 9:
                # 16-bit signed short
                self._convert_to_short(raw_data)
            
            print("Screen capture successful")
        except Exception as e:
            print(f"Screen capture failed: {str(e)}")
            sys.exit(1)
    
    def _convert_bgra_to_argb(self, raw_data):
        """Convert BGRA to ARGB format"""
        for i in range(0, len(raw_data), 4):
            self.data[i] = raw_data[i+3]    # A
            self.data[i+1] = raw_data[i+2]  # R
            self.data[i+2] = raw_data[i+1]  # G
            self.data[i+3] = raw_data[i]    # B
    
    def _convert_to_5551(self, raw_data):
        """Convert to 16-bit 5-5-5-1 format"""
        for i in range(0, len(raw_data), 4):
            r = raw_data[i+2] >> 3
            g = raw_data[i+1] >> 3
            b = raw_data[i] >> 3
            a = 1 if raw_data[i+3] > 127 else 0
            packed = (r << 11) | (g << 6) | (b << 1) | a
            struct.pack_into('H', self.data, i//2, packed)
    
    def _convert_to_1555_rev(self, raw_data):
        """Convert to 16-bit 1-5-5-5 reversed format"""
        for i in range(0, len(raw_data), 4):
            a = raw_data[i+3] >> 7
            b = raw_data[i] >> 3
            g = raw_data[i+1] >> 3
            r = raw_data[i+2] >> 3
            packed = (a << 15) | (b << 10) | (g << 5) | r
            struct.pack_into('H', self.data, i//2, packed)
    
    def _convert_to_8888(self, raw_data):
        """Convert to 32-bit 8-8-8-8 format"""
        for i in range(0, len(raw_data), 4):
            packed = (raw_data[i+3] << 24) | (raw_data[i+2] << 16) | (raw_data[i+1] << 8) | raw_data[i]
            struct.pack_into('I', self.data, i, packed)
    
    def _convert_to_8888_rev(self, raw_data):
        """Convert to 32-bit 8-8-8-8 reversed format"""
        for i in range(0, len(raw_data), 4):
            packed = (raw_data[i] << 24) | (raw_data[i+1] << 16) | (raw_data[i+2] << 8) | raw_data[i+3]
            struct.pack_into('I', self.data, i, packed)
    
    def _convert_to_1010102(self, raw_data):
        """Convert to 32-bit 10-10-10-2 format"""
        for i in range(0, len(raw_data), 4):
            r = raw_data[i+2] >> 2
            g = raw_data[i+1] >> 2
            b = raw_data[i] >> 2
            a = raw_data[i+3] >> 6
            packed = (r << 22) | (g << 12) | (b << 2) | a
            struct.pack_into('I', self.data, i, packed)
    
    def _convert_to_2101010_rev(self, raw_data):
        """Convert to 32-bit 2-10-10-10 reversed format"""
        for i in range(0, len(raw_data), 4):
            a = raw_data[i+3] >> 6
            r = raw_data[i+2] >> 2
            g = raw_data[i+1] >> 2
            b = raw_data[i] >> 2
            packed = (a << 30) | (r << 20) | (g << 10) | b
            struct.pack_into('I', self.data, i, packed)
    
    def _convert_to_ushort(self, raw_data):
        """Convert to 16-bit unsigned short format"""
        for i in range(0, len(raw_data), 4):
            # Simple averaging of RGB to 16-bit
            val = (raw_data[i+2] + raw_data[i+1] + raw_data[i]) // 3
            packed = val << 8 | val
            struct.pack_into('H', self.data, i//2, packed)
    
    def _convert_to_short(self, raw_data):
        """Convert to 16-bit signed short format"""
        for i in range(0, len(raw_data), 4):
            # Simple averaging of RGB to signed 16-bit
            val = (raw_data[i+2] + raw_data[i+1] + raw_data[i]) // 3 - 128
            packed = val & 0xFFFF
            struct.pack_into('h', self.data, i//2, packed)
    
    def manipulate_buffer(self, safe_mode=False, glitches=None):
        """Apply glitch effects to the buffer"""
        if glitches is None:
            glitches = 158 if safe_mode else random.randint(1, 200)
        
        print(f"Applying {glitches} glitch effects...")
        
        for i in range(glitches):
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
                    print(f"Progress: {i+1}/{glitches} glitches applied")
            except Exception as e:
                print(f"Error applying glitch: {str(e)}")
                continue
        
        print("Glitch effects complete")
    
    def _apply_glitch(self, x, y, width, height, safe_mode):
        """Apply a simple glitch effect to a region"""
        # Filter available modes based on enabled glitches
        available_modes = [m for m in range(10) if m in self.enabled_simple_glitches]
        
        # If no modes are enabled, return without doing anything
        if not available_modes:
            return
            
        # Select a random mode from available ones
        mode = random.choice(available_modes)
        
        for row in range(y, min(y + height, self.height)):
            offset = row * self.byte_width + x * 4
            end = min(offset + width * 4, len(self.data))
            
            if mode == 0:  # swap-channels
                # Swap color channels (only if we have enough bytes)
                for i in range(offset, end - 2, 4):
                    self.data[i], self.data[i+1], self.data[i+2] = \
                        self.data[i+2], self.data[i], self.data[i+1]
            elif mode == 1:  # invert-colors
                # Invert colors
                for i in range(offset, end - 2, 4):
                    self.data[i] = 255 - self.data[i]
                    self.data[i+1] = 255 - self.data[i+1]
                    self.data[i+2] = 255 - self.data[i+2]
            elif mode == 2:  # channel-shift
                # Random channel shift
                for i in range(offset, end - 2, 4):
                    shift = random.randint(1, 3)
                    self.data[i], self.data[i+1], self.data[i+2] = \
                        self.data[(i+shift)%end], self.data[(i+1+shift)%end], self.data[(i+2+shift)%end]
            elif mode == 3:  # channel-separation
                # Channel separation
                for i in range(offset, end - 2, 4):
                    self.data[i] = min(self.data[i] + 50, 255)
                    self.data[i+1] = max(self.data[i+1] - 50, 0)
            elif mode == 4:  # pixel-sorting
                # Pixel sorting
                for i in range(offset, end - 2, 4):
                    channels = [self.data[i], self.data[i+1], self.data[i+2]]
                    channels.sort()
                    self.data[i], self.data[i+1], self.data[i+2] = channels
            elif mode == 5:  # random-noise
                # Random noise
                for i in range(offset, end - 2, 4):
                    if random.random() < 0.3:
                        self.data[i] = random.randint(0, 255)
                        self.data[i+1] = random.randint(0, 255)
                        self.data[i+2] = random.randint(0, 255)
            elif mode == 6:  # channel-wrap
                # Channel shift with wrap
                for i in range(offset, end - 2, 4):
                    self.data[i], self.data[i+1], self.data[i+2] = \
                        self.data[i+1], self.data[i+2], self.data[i]
            elif mode == 7:  # extreme-contrast
                # Extreme contrast
                for i in range(offset, end - 2, 4):
                    self.data[i] = 255 if self.data[i] > 127 else 0
                    self.data[i+1] = 255 if self.data[i+1] > 127 else 0
                    self.data[i+2] = 255 if self.data[i+2] > 127 else 0
            elif mode == 8:  # color-reduction
                # 16-bit style color reduction
                for i in range(offset, end - 2, 4):
                    self.data[i] = self.data[i] & 0xF8
                    self.data[i+1] = self.data[i+1] & 0xFC
                    self.data[i+2] = self.data[i+2] & 0xF8
            elif mode == 9:  # channel-zeroing
                # Random channel zeroing
                for i in range(offset, end - 2, 4):
                    if random.random() < 0.2:
                        self.data[i] = 0
                    if random.random() < 0.2:
                        self.data[i+1] = 0
                    if random.random() < 0.2:
                        self.data[i+2] = 0
    
    def _apply_complex_glitch(self, x, y, width, height, safe_mode):
        """Apply more complex glitch effects to a region"""
        # Filter available modes based on enabled glitches
        available_modes = [m for m in range(6) if m in self.enabled_complex_glitches]
        
        # If no modes are enabled, return without doing anything
        if not available_modes:
            return
            
        # Select a random mode from available ones
        mode = random.choice(available_modes)
        
        for row in range(y, min(y + height, self.height)):
            offset = row * self.byte_width + x * 4
            end = min(offset + width * 4, len(self.data))
            
            if mode == 0:  # pixel-sort-effect
                # Pixel sorting effect
                for i in range(offset, end - 2, 4):
                    # Sort RGB channels by value
                    channels = [self.data[i], self.data[i+1], self.data[i+2]]
                    channels.sort()
                    self.data[i], self.data[i+1], self.data[i+2] = channels
            elif mode == 1:  # data-bending
                # Data bending effect
                for i in range(offset, end - 2, 4):
                    # Randomly shift pixel data
                    shift = random.randint(1, 3)
                    self.data[i], self.data[i+1], self.data[i+2] = \
                        self.data[(i+shift)%end], self.data[(i+1+shift)%end], self.data[(i+2+shift)%end]
            elif mode == 2:  # noise-injection
                # Noise injection
                for i in range(offset, end - 2, 4):
                    if random.random() < 0.3:
                        self.data[i] = random.randint(0, 255)
                        self.data[i+1] = random.randint(0, 255)
                        self.data[i+2] = random.randint(0, 255)
            elif mode == 3:  # channel-manipulation
                # Extreme channel manipulation
                for i in range(offset, end - 2, 4):
                    # Randomly zero out channels
                    if random.random() < 0.2:
                        self.data[i] = 0
                    if random.random() < 0.2:
                        self.data[i+1] = 0
                    if random.random() < 0.2:
                        self.data[i+2] = 0
            elif mode == 4:  # block-transfer
                # Block transfer effect
                block_size = random.randint(4, 32)
                for i in range(offset, end - block_size, block_size):
                    src = random.randint(offset, end - block_size)
                    self.data[i:i+block_size] = self.data[src:src+block_size]
            elif mode == 5:  # scanline-effect
                # Scanline effect
                for i in range(offset, end - 2, 4):
                    if row % 2 == 0:
                        self.data[i] = self.data[i] // 2
                        self.data[i+1] = self.data[i+1] // 2
                        self.data[i+2] = self.data[i+2] // 2
    
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
    
    def run(self, safe_mode=False, glitches=None):
        """Main execution method"""
        try:
            self.capture_screen(safe_mode)
            self.manipulate_buffer(safe_mode, glitches)
            saved_path = self.save_image()
            return saved_path
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            sys.exit(0)

def print_help():
    """Print custom help message with all available options"""
    help_text = """
ScreenFvck - Glitch Screen Capture Tool
======================================

USAGE:
  ./screenfuck.py [OPTIONS]

BASIC OPTIONS:
  --help                  Show this help message and exit
  --safe                  Use safe mode (fewer glitch types)
  --glitches NUMBER       Number of glitches to apply (default: 158 in safe mode, random 1-200 otherwise)

SIMPLE GLITCH METHODS:
  --enable-swap-channels       Enable swap-channels glitch method
  --disable-swap-channels      Disable swap-channels glitch method
  --enable-invert-colors       Enable invert-colors glitch method
  --disable-invert-colors      Disable invert-colors glitch method
  --enable-channel-shift       Enable channel-shift glitch method
  --disable-channel-shift      Disable channel-shift glitch method
  --enable-channel-separation  Enable channel-separation glitch method
  --disable-channel-separation Disable channel-separation glitch method
  --enable-pixel-sorting       Enable pixel-sorting glitch method
  --disable-pixel-sorting      Disable pixel-sorting glitch method
  --enable-random-noise        Enable random-noise glitch method
  --disable-random-noise       Disable random-noise glitch method
  --enable-channel-wrap        Enable channel-wrap glitch method
  --disable-channel-wrap       Disable channel-wrap glitch method
  --enable-extreme-contrast    Enable extreme-contrast glitch method
  --disable-extreme-contrast   Disable extreme-contrast glitch method
  --enable-color-reduction     Enable color-reduction glitch method
  --disable-color-reduction    Disable color-reduction glitch method
  --enable-channel-zeroing     Enable channel-zeroing glitch method
  --disable-channel-zeroing    Disable channel-zeroing glitch method

COMPLEX GLITCH METHODS:
  --enable-pixel-sort-effect   Enable pixel-sort-effect glitch method
  --disable-pixel-sort-effect  Disable pixel-sort-effect glitch method
  --enable-data-bending        Enable data-bending glitch method
  --disable-data-bending       Disable data-bending glitch method
  --enable-noise-injection     Enable noise-injection glitch method
  --disable-noise-injection    Disable noise-injection glitch method
  --enable-channel-manipulation Enable channel-manipulation glitch method
  --disable-channel-manipulation Disable channel-manipulation glitch method
  --enable-block-transfer      Enable block-transfer glitch method
  --disable-block-transfer     Disable block-transfer glitch method
  --enable-scanline-effect     Enable scanline-effect glitch method
  --disable-scanline-effect    Disable scanline-effect glitch method

NOTE: For compatibility, you can use either dashes or underscores in method names:
  --enable-random-noise and --enable-random_noise are both accepted

EXAMPLES:
  ./screenfuck.py                     # Run with default settings
  ./screenfuck.py --safe              # Run in safe mode
  ./screenfuck.py --glitches 50       # Apply exactly 50 glitches
  ./screenfuck.py --enable-random-noise --enable-scanline-effect  # Only use these two effects
  ./screenfuck.py --disable-channel-zeroing --disable-block-transfer  # Use all effects except these two
"""
    print(help_text)
    sys.exit(0)

# Custom argument parser that handles both dash and underscore formats
class CustomArgumentParser(argparse.ArgumentParser):
    def _parse_optional(self, arg_string):
        # Check if this is a method flag with underscores
        if arg_string.startswith(('--enable-', '--disable-')) and '_' in arg_string:
            # Convert to dash format
            dash_arg = arg_string.replace('_', '-')
            # Check if we have this argument
            if dash_arg in self._option_string_actions:
                # Use the dash version instead
                return super()._parse_optional(dash_arg)
        
        # Default behavior
        return super()._parse_optional(arg_string)

if __name__ == "__main__":
    print("Starting ScreenFvck (Python version)")
    
    # Check for help flag first
    if "--help" in sys.argv:
        print_help()
    
    # Set up argument parser
    parser = CustomArgumentParser(description='ScreenFvck - glitch screen capture tool', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show this help message and exit')
    parser.add_argument('--safe', action='store_true', help='Use safe mode (fewer glitch types)')
    parser.add_argument('--glitches', type=int, help='Number of glitches to apply')
    
    # Add enable/disable arguments for each glitch method
    simple_group = parser.add_argument_group('Simple glitch methods')
    complex_group = parser.add_argument_group('Complex glitch methods')
    
    for method in ScreenFuck.SIMPLE_GLITCH_METHODS:
        simple_group.add_argument(f'--enable-{method}', action='store_true', 
                                 help=f'Enable {method} glitch method')
        simple_group.add_argument(f'--disable-{method}', action='store_true',
                                 help=f'Disable {method} glitch method')
    
    for method in ScreenFuck.COMPLEX_GLITCH_METHODS:
        complex_group.add_argument(f'--enable-{method}', action='store_true',
                                  help=f'Enable {method} glitch method')
        complex_group.add_argument(f'--disable-{method}', action='store_true',
                                  help=f'Disable {method} glitch method')
    
    args = parser.parse_args()
    
    # Show help if requested
    if args.help:
        print_help()
    
    sf = ScreenFuck()
    
    # Process enable/disable flags
    enabled_methods = []
    disabled_methods = []
    
    # Check for enabled methods
    for method in ScreenFuck.SIMPLE_GLITCH_METHODS + ScreenFuck.COMPLEX_GLITCH_METHODS:
        # Convert dashes to underscores for argparse
        arg_name = method.replace('-', '_')
        enable_arg = f'enable_{arg_name}'
        disable_arg = f'disable_{arg_name}'
        
        if hasattr(args, enable_arg) and getattr(args, enable_arg):
            enabled_methods.append(method)
        if hasattr(args, disable_arg) and getattr(args, disable_arg):
            disabled_methods.append(method)
    
    # Set enabled/disabled methods
    if enabled_methods or disabled_methods:
        sf.set_enabled_glitches(enabled_methods, disabled_methods)
    
    # Run with specified options
    saved_path = sf.run(safe_mode=args.safe, glitches=args.glitches)
    print(f"Glitched screenshot successfully saved to: {saved_path}")
