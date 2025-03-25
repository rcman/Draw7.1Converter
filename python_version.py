import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import tempfile
import io

class STDViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("STD File Viewer")
        self.geometry("900x700")
        
        # Store loaded images and file info
        self.images = []
        self.photo_images = []
        self.current_files = []
        self.sheet_photo_refs = []
        self.temp_files = []  # To track temporary files
        
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
        
        # Create a notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create first tab for image grid view
        self.grid_frame = tk.Frame(self.notebook)
        self.notebook.add(self.grid_frame, text="Grid View")
        
        # Create a canvas with scrollbar for displaying images
        self.canvas_frame = tk.Frame(self.grid_frame)
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
        
        # Create second tab for sprite sheet view of a single file
        self.sheet_frame = tk.Frame(self.notebook)
        self.notebook.add(self.sheet_frame, text="Sprite Sheet View")
        
        # File selection for sprite sheet view
        self.file_select_frame = tk.Frame(self.sheet_frame)
        self.file_select_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.lbl_file = tk.Label(self.file_select_frame, text="Select file:")
        self.lbl_file.pack(side=tk.LEFT, padx=5)
        
        self.file_var = tk.StringVar()
        self.file_dropdown = ttk.Combobox(self.file_select_frame, textvariable=self.file_var, state="readonly")
        self.file_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.file_dropdown.bind("<<ComboboxSelected>>", self.on_file_selected)
        
        # Canvas for sprite sheet display
        self.sheet_canvas_frame = tk.Frame(self.sheet_frame)
        self.sheet_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.sheet_canvas = tk.Canvas(self.sheet_canvas_frame, bg="white")
        self.sheet_scrollbar_y = tk.Scrollbar(self.sheet_canvas_frame, orient=tk.VERTICAL, command=self.sheet_canvas.yview)
        self.sheet_scrollbar_x = tk.Scrollbar(self.sheet_canvas_frame, orient=tk.HORIZONTAL, command=self.sheet_canvas.xview)
        
        self.sheet_canvas.configure(yscrollcommand=self.sheet_scrollbar_y.set, xscrollcommand=self.sheet_scrollbar_x.set)
        
        self.sheet_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.sheet_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.sheet_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configure canvas scrolling
        self.image_frame.bind("<Configure>", self.on_frame_configure)
        self.sheet_canvas.bind("<Configure>", self.on_sheet_canvas_configure)
        
    def on_frame_configure(self, event):
        # Update the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def on_sheet_canvas_configure(self, event):
        # Update the scroll region for sheet canvas
        self.sheet_canvas.configure(scrollregion=self.sheet_canvas.bbox("all"))
        
    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.lbl_dir.config(text=directory)
            self.scan_directory(directory)
    
    def cleanup_temp_files(self):
        """Clean up any temporary files we created"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"Error removing temp file {temp_file}: {e}")
        self.temp_files = []
    
    def pil_to_tkimage(self, pil_image):
        """Convert PIL Image to Tkinter PhotoImage without ImageTk"""
        # Create a temporary file for the image
        with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as temp_file:
            temp_filename = temp_file.name
            self.temp_files.append(temp_filename)
            
        # Save the PIL image as GIF (with transparency)
        pil_image.save(temp_filename, 'GIF')
        
        # Open with Tkinter's PhotoImage
        photo = tk.PhotoImage(file=temp_filename)
        return photo
    
    def scan_directory(self, directory):
        # Clear previous images
        for widget in self.image_frame.winfo_children():
            widget.destroy()
        
        # Clean up previous temp files
        self.cleanup_temp_files()
        
        # Clear previous references to ensure proper garbage collection
        self.images = []
        self.photo_images = []
        self.current_files = []
        self.sheet_photo_refs = []
        
        # Find all .STD files
        std_files = []
        for file in os.listdir(directory):
            if file.lower().endswith('.std'):
                std_files.append(os.path.join(directory, file))
        
        if not std_files:
            messagebox.showinfo("No Files", "No .STD files found in the selected directory")
            self.status_var.set("No .STD files found")
            self.file_dropdown['values'] = []
            return
        
        self.status_var.set(f"Found {len(std_files)} .STD files. Processing...")
        self.update()
        
        # Process each STD file
        row, col = 0, 0
        max_cols = 5  # Number of images per row
        
        for std_file in std_files:
            try:
                # Extract first image from STD file
                img = self.extract_first_image(std_file)
                if img:
                    # Store the file path
                    self.current_files.append(std_file)
                    
                    # Scale up the image for better visibility
                    img_scaled = img.resize((64, 64), Image.NEAREST)
                    
                    # Convert to tkinter PhotoImage
                    photo = self.pil_to_tkimage(img_scaled)
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
        
        # Update the grid layout after processing all files
        self.image_frame.update_idletasks()
        
        # Update the file dropdown
        self.file_dropdown['values'] = [os.path.basename(f) for f in self.current_files]
        if self.current_files:
            self.file_dropdown.current(0)
            self.on_file_selected(None)
            
        self.status_var.set(f"Loaded {len(self.photo_images)} images from {len(std_files)} .STD files")
    
    def on_file_selected(self, event):
        selected_file = self.file_var.get()
        if selected_file:
            file_path = next((f for f in self.current_files if os.path.basename(f) == selected_file), None)
            if file_path:
                self.show_sprite_sheet(file_path)
    
    def show_sprite_sheet(self, file_path):
        # Clear previous content
        self.sheet_canvas.delete("all")
        
        try:
            # Load all sprites from the file
            sprites = self.extract_all_images(file_path)
            if not sprites:
                self.status_var.set(f"No valid sprites found in {os.path.basename(file_path)}")
                return
                
            # Arrange sprites in a grid (10 per row)
            sprites_per_row = 10
            padding = 5
            sprite_size = 64  # Display size
            
            # Create a frame for the sprites
            sheet_frame = tk.Frame(self.sheet_canvas)
            self.sheet_canvas.create_window(0, 0, window=sheet_frame, anchor=tk.NW)
            
            # Display each sprite
            self.sheet_photo_refs = []  # Store references to prevent garbage collection
            for i, sprite in enumerate(sprites):
                if sprite:
                    row = i // sprites_per_row
                    col = i % sprites_per_row
                    
                    # Scale up the sprite
                    sprite_scaled = sprite.resize((sprite_size, sprite_size), Image.NEAREST)
                    photo = self.pil_to_tkimage(sprite_scaled)
                    self.sheet_photo_refs.append(photo)
                    
                    # Create a frame for each sprite
                    sprite_frame = tk.Frame(sheet_frame)
                    sprite_frame.grid(row=row, column=col, padx=padding, pady=padding)
                    
                    # Display sprite
                    sprite_label = tk.Label(sprite_frame, image=photo)
                    sprite_label.pack()
                    
                    # Display sprite number
                    num_label = tk.Label(sprite_frame, text=f"#{i}")
                    num_label.pack()
            
            # Update canvas scrolling
            sheet_frame.update_idletasks()
            self.sheet_canvas.configure(scrollregion=self.sheet_canvas.bbox("all"))
            
            self.status_var.set(f"Loaded {len(sprites)} sprites from {os.path.basename(file_path)}")
            
        except Exception as e:
            self.status_var.set(f"Error displaying sprite sheet: {e}")
    
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
                
                return self.create_image_from_pixel_data(pixel_data)
                
        except Exception as e:
            print(f"Error reading {std_file}: {e}")
            return None
    
    def extract_all_images(self, std_file):
        """
        Extract all 16x16 pixel images from an STD file.
        """
        sprites = []
        try:
            with open(std_file, 'rb') as f:
                file_data = f.read()
                
                # Extract sprites (each is 256 bytes)
                sprite_size = 256
                for i in range(0, len(file_data), sprite_size):
                    if i + sprite_size <= len(file_data):
                        pixel_data = file_data[i:i+sprite_size]
                        sprite = self.create_image_from_pixel_data(pixel_data)
                        sprites.append(sprite)
            
            return sprites
                
        except Exception as e:
            print(f"Error extracting sprites from {std_file}: {e}")
            return []
    
    def create_image_from_pixel_data(self, pixel_data):
        """
        Create a PIL Image from raw pixel data using the appropriate color palette.
        """
        # Create a new RGB image
        img = Image.new('RGB', (16, 16))
        pixels = []
        
        # Convert each byte to an RGB value using a VGA-style color palette
        # This palette is based on the standard 16-color VGA palette
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
        
        # Process each pixel
        for y in range(16):
            for x in range(16):
                index = y * 16 + x
                if index < len(pixel_data):
                    # Get color index (limit to 0-15 to avoid index errors)
                    color_index = pixel_data[index] & 0x0F
                    if color_index < 0 or color_index >= len(color_palette):
                        color_index = 0
                    
                    # Assign RGB color to pixel
                    pixels.append(color_palette[color_index])
                else:
                    # Default to black if data is missing
                    pixels.append((0, 0, 0))
        
        # Populate the image with pixels
        img.putdata(pixels)
        return img
    
    def __del__(self):
        """Destructor to ensure temp files are cleaned up"""
        self.cleanup_temp_files()

if __name__ == "__main__":
    app = STDViewer()
    app.mainloop()
