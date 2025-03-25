import pygame
import sys
import os
from pygame import Surface
from tkinter import messagebox
import tkinter as tk

# Initialize arrays
images = [None] * 100
count = 0

def load_std_file(filename):
    """Load sprites from an STD file format"""
    try:
        with open(filename, "rb") as fp:
            for sprite_index in range(100):
                # Each sprite is 16x16 pixels
                for y in range(16):
                    for x in range(16):
                        # Get pixel value from file
                        color_index = int.from_bytes(fp.read(1), byteorder='little')
                        
                        # Set pixel value (assuming grayscale conversion)
                        r, g, b = color_index, color_index, color_index
                        images[sprite_index].set_at((x, y), (r, g, b, 255))
        return True
    except Exception as e:
        print(f"Failed to load file: {filename}. Error: {e}")
        return False

def main():
    global count, images
    
    # Check command line arguments
    if len(sys.argv) < 3:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showinfo("STDCNV.PY", 
                           "use: python stdcnv.py STDFILE SAVEDIR\nProgrammed by Richard Marks - 9:04 PM 11-15-04\nPython conversion by Claude")
        root.destroy()
        return -1
    
    std_file = sys.argv[1]
    save_dir = sys.argv[2]
    
    # Initialize pygame
    pygame.init()
    
    # Create window
    window_title = f"STDCNV.PY -> [{std_file}] : Press ESC to quit"
    window = pygame.display.set_mode((640, 480))
    pygame.display.set_caption(window_title)
    
    # Initialize all surfaces
    for index in range(100):
        images[index] = pygame.Surface((16, 16), pygame.SRCALPHA)
    
    # Load STD file
    if not load_std_file(std_file):
        pygame.quit()
        return -1
    
    # Create display of sprites
    window.fill((0, 0, 0))
    
    # Display sprites in a grid
    for y in range(10):
        for x in range(10):
            index = x + y * 10
            # Scale sprite to 32x32 for display
            scaled_sprite = pygame.transform.scale(images[index], (32, 32))
            window.blit(scaled_sprite, (x * 32, y * 32))
    
    pygame.display.flip()
    
    # Ensure save directory exists
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Save all bitmaps
    for i in range(100):
        bmp_path = os.path.join(save_dir, f"{os.path.basename(save_dir)}_{i}.bmp")
        try:
            pygame.image.save(images[i], bmp_path)
            count += 1
        except Exception as e:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Save Error", 
                                f"Error saving bitmap #{i} to {bmp_path}: {e}")
            root.destroy()
    
    # Show success message
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Success", f"Saved {count} bitmaps in {save_dir}")
    root.destroy()
    
    # Main loop - wait for ESC key
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
    
    # Clean up
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
