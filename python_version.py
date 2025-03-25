import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import struct

class STDViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("STD File Viewer")
        self.geometry("800x600")
        
        # Store loaded images
        self.images = []
        self.photo_images = []
        
        # Create UI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Top frame for controls
        control_frame = tk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Button to select directory
        self.btn_select = tk.Button(control_frame, text="Select Directory", command=self.select_directory)
        self.btn_select.pack(side=tk.LEFT, padx=5)
        
        # Label to show selected directory
        self.lbl_dir = tk.Label(control_frame, text="No directory selected")
        self.lbl_dir.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Create a canvas with scrollbar for displaying images
        self.canvas_frame = tk.Frame(self)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.scrollbar_y = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar_x = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a frame inside the canvas for image display
        self.image_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.image_frame, anchor=tk.NW)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configure canvas scrolling
        self.image_frame.bind("<Configure>", self.on_frame_configure)
        
    def on_frame_configure(self, event):
        # Update the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.lbl_dir.config(text=directory)
            self.scan_directory(directory)
    
    def scan_directory(self, directory):
        # Clear previous images
        for widget in self.image_frame.winfo_children():
            widget.destroy()
        
        self.images = []
        self.photo_images = []
        
        # Find all .STD files
        std_files = []
        for file in os.listdir(directory):
            if file.lower().endswith('.std'):
                std_files.append(os.path.join(directory, file))
        
        if not std_files:
            messagebox.showinfo("No Files", "No .STD files found in the selected directory")
            self.status_var.set("No .STD files found")
            return
        
        self.status_var.set(f"Found {len(std_files)} .STD files. Processing...")
        self.update()
        
        # Process each STD file
        row, col = 0, 0
        max_cols = 5  # Number of images per row
        
        for std_file in std_files:
            try:
                # Extract first image from STD file
                # Based on the original C code, we know each file can contain multiple 16x16 images
                # But we only want to show the first image from each file
                img = self.extract_first_image(std_file)
                if img:
                    # Scale up the image for better visibility
                    img_scaled = img.resize((64, 64), Image.NEAREST)
                    
                    # Convert to PhotoImage
                    photo = ImageTk.PhotoImage(img_scaled)
                    self.photo_images.append(photo)  # Keep a reference
                    
                    # Create a frame for the image and its label
                    img_container = tk.Frame(self.image_frame, padx=5, pady=5)
                    img_container.grid(row=row, column=col, padx=5, pady=5)
                    
                    # Display the image
                    img_label = tk.Label(img_container, image=photo)
                    img_label.pack()
                    
                    # Display the filename
                    filename = os.path.basename(std_file)
                    text_label = tk.Label(img_container, text=filename)
                    text_label.pack()
                    
                    # Update grid position
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
            except Exception as e:
                print(f"Error processing {std_file}: {e}")
        
        self.status_var.set(f"Loaded {len(self.photo_images)} images from {len(std_files)} .STD files")
    
    def extract_first_image(self, std_file):
        """
        Extract the first 16x16 pixel image from an STD file.
        Based on the original C code, we know that:
        - Each image in the STD file is 256 bytes (16x16 pixels with 1 byte per pixel)
        - Each file can contain multiple images (up to 100 - 10 rows of 10 objects)
        """
        try:
            with open(std_file, 'rb') as f:
                # From the C code, we can see that each image is 256 bytes (16*16)
                image_size = 256
                pixel_data = f.read(image_size)
                
                if len(pixel_data) < image_size:
                    return None  # Not enough data
                
                # Create a new RGB image
                img = Image.new('RGB', (16, 16))
                pixels = []
                
                # Convert each byte to an RGB value using a color palette
                # This uses a standard 16-color palette that would have been common in older graphics
                color_palette = [
                    (0, 0, 0),       # 0: Black
                    (0, 0, 170),     # 1: Blue
                    (0, 170, 0),     # 2: Green
                    (0, 170, 170),   # 3: Cyan
                    (170, 0, 0),     # 4: Red
                    (170, 0, 170),   # 5: Magenta
                    (170, 85, 0),    # 6: Brown
                    (170, 170, 170), # 7: Light Gray
                    (85, 85, 85),    # 8: Dark Gray
                    (85, 85, 255),   # 9: Light Blue
                    (85, 255, 85),   # 10: Light Green
                    (85, 255, 255),  # 11: Light Cyan
                    (255, 85, 85),   # 12: Light Red
                    (255, 85, 255),  # 13: Light Magenta
                    (255, 255, 85),  # 14: Yellow
                    (255, 255, 255)  # 15: White
                ]
                
                # Build the image pixel by pixel
                x, y = 0, 0
                for byte in pixel_data:
                    # Convert the byte to an integer if needed
                    value = byte if isinstance(byte, int) else ord(byte)
                    
                    # Use the value to index into the color palette
                    # Make sure the value is within the range of our palette
                    color_index = value % len(color_palette)
                    pixels.append(color_palette[color_index])
                    
                    # Move to the next position
                    x += 1
                    if x >= 16:
                        x = 0
                        y += 1
                
                img.putdata(pixels)
                return img
                
        except Exception as e:
            print(f"Error reading {std_file}: {e}")
            return None

if __name__ == "__main__":
    app = STDViewer()
    app.mainloop()
