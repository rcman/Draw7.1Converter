import os
import sys
import struct
import numpy as np
import pygame
from pygame.locals import *
from pathlib import Path

class DOSAnimObject:
    """Class representing animation object structure from the original code"""
    def __init__(self):
        self.active = 0
        self.animwidth = 0
        self.animheight = 0
        self.animox = 0
        self.animoy = 0
        self.animx = 0
        self.animy = 0
        self.prox = 0
        self.animspeed = 0
        self.currentshape = 0
        self.oldshape = 0
        self.max = 0
        self.row = 0
        
class DOSShape:
    """Class representing a shape from the original code"""
    def __init__(self):
        self.w = 0
        self.h = 0
        self.n = 0
        self.c = 0
        self.flag = 0
        self.rowflag = 0
        self.shp = np.zeros((16, 16), dtype=np.uint8)

class DOSSpriteViewer:
    def __init__(self, directory="."):
        """Initialize the sprite viewer with the directory to scan."""
        self.directory = directory
        self.std_files = []
        self.sprites = {}
        self.current_file_base = None
        self.current_sprite_index = 0
        self.current_row = 0
        self.zoom = 8  # Scale factor for pixels
        self.grid_rows = 5
        self.grid_cols = 10
        self.view_mode = "sprite"  # "sprite", "grid", "layout"
        
        # Animation objects and layout data from the original program
        self.anim_objects = [DOSAnimObject() for _ in range(10)]  # TOTALANIMS = 10
        self.sprites_data = [[DOSShape() for _ in range(10)] for _ in range(10)]  # TOTALSHAPE = 10, TOTALANIMS = 10
        self.layout = [[-1 for _ in range(100)] for _ in range(100)]  # Layout grid from original code
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption("DOS Sprite Viewer")
        self.font = pygame.font.SysFont('Arial', 16)
        self.clock = pygame.time.Clock()
        
        # Default color palette - EGA/VGA 16 colors
        self.palette = [
            (0, 0, 0),         # 0: Black
            (0, 0, 170),       # 1: Blue
            (0, 170, 0),       # 2: Green
            (0, 170, 170),     # 3: Cyan
            (170, 0, 0),       # 4: Red
            (170, 0, 170),     # 5: Magenta
            (170, 85, 0),      # 6: Brown
            (170, 170, 170),   # 7: Light Gray
            (85, 85, 85),      # 8: Dark Gray
            (85, 85, 255),     # 9: Light Blue
            (85, 255, 85),     # 10: Light Green
            (85, 255, 255),    # 11: Light Cyan
            (255, 85, 85),     # 12: Light Red
            (255, 85, 255),    # 13: Light Magenta
            (255, 255, 85),    # 14: Yellow
            (255, 255, 255)    # 15: White
        ]
        
        # Extend palette to 256 colors (for VGA)
        for i in range(16, 256):
            # Create a gradient of colors for the extended palette
            r = (i % 6) * 51
            g = ((i // 6) % 6) * 51
            b = ((i // 36) % 6) * 51
            self.palette.append((r, g, b))
        
    def scan_directory(self):
        """Scan the directory for .std files (case-insensitive)"""
        path = Path(self.directory)
        # Look for both lowercase and uppercase extensions
        lowercase_files = list(path.glob("*.std"))
        uppercase_files = list(path.glob("*.STD"))
        
        # Combine the results
        self.std_files = lowercase_files + uppercase_files
        print(f"Found {len(self.std_files)} .std files")
        
        # Extract base filenames without extensions
        self.base_filenames = [file.stem for file in self.std_files]
        
        return len(self.std_files) > 0
    
    def load_file_set(self, base_filename):
        """Load a complete set of files (.std, .inf, .map, .dat) for a given base filename"""
        self.current_file_base = base_filename
        success = True
        
        # Reset data structures
        self.anim_objects = [DOSAnimObject() for _ in range(10)]
        self.sprites_data = [[DOSShape() for _ in range(10)] for _ in range(10)]
        self.layout = [[-1 for _ in range(100)] for _ in range(100)]
        self.sprites = {}
        
        # Try different case variations for .std file extension
        std_path_lower = Path(self.directory) / f"{base_filename}.std"
        std_path_upper = Path(self.directory) / f"{base_filename}.STD"
        
        if std_path_lower.exists():
            print(f"Loading STD file: {std_path_lower}")
            success &= self.load_std_file(std_path_lower)
        elif std_path_upper.exists():
            print(f"Loading STD file: {std_path_upper}")
            success &= self.load_std_file(std_path_upper)
        else:
            print(f"STD file not found: {base_filename}.std or {base_filename}.STD")
            success = False
        
        # Load .inf file (shape metadata) - try both cases
        inf_path_lower = Path(self.directory) / f"{base_filename}.inf"
        inf_path_upper = Path(self.directory) / f"{base_filename}.INF"
        
        if inf_path_lower.exists():
            print(f"Loading INF file: {inf_path_lower}")
            success &= self.load_inf_file(inf_path_lower)
        elif inf_path_upper.exists():
            print(f"Loading INF file: {inf_path_upper}")
            success &= self.load_inf_file(inf_path_upper)
        else:
            print(f"INF file not found: {base_filename}.inf or {base_filename}.INF")
            # Not required for basic viewing, so don't set success to False
        
        # Load .map file (layout data) - try both cases
        map_path_lower = Path(self.directory) / f"{base_filename}.map"
        map_path_upper = Path(self.directory) / f"{base_filename}.MAP"
        
        if map_path_lower.exists():
            print(f"Loading MAP file: {map_path_lower}")
            success &= self.load_map_file(map_path_lower)
        elif map_path_upper.exists():
            print(f"Loading MAP file: {map_path_upper}")
            success &= self.load_map_file(map_path_upper)
        else:
            print(f"MAP file not found: {base_filename}.map or {base_filename}.MAP")
            # Not required for basic viewing, so don't set success to False
        
        # Load .dat file (animation object data) - try both cases
        dat_path_lower = Path(self.directory) / f"{base_filename}.dat"
        dat_path_upper = Path(self.directory) / f"{base_filename}.DAT" 
        
        if dat_path_lower.exists():
            print(f"Loading DAT file: {dat_path_lower}")
            success &= self.load_dat_file(dat_path_lower)
        elif dat_path_upper.exists():
            print(f"Loading DAT file: {dat_path_upper}")
            success &= self.load_dat_file(dat_path_upper)
        else:
            print(f"DAT file not found: {base_filename}.dat or {base_filename}.DAT")
            # Not required for basic viewing, so don't set success to False
        
        self.current_sprite_index = 0
        self.current_row = 0
        return success
        
    def load_std_file(self, file_path):
        """Load a .std file containing raw sprite data"""
        try:
            with open(file_path, "rb") as f:
                data = f.read()
                
            # Each sprite is 256 bytes (16x16 pixels)
            sprite_count = len(data) // 256
            self.sprites = {}
            
            for i in range(sprite_count):
                sprite_data = data[i*256:(i+1)*256]
                # Convert to 16x16 array
                sprite = np.zeros((16, 16), dtype=np.uint8)
                for y in range(16):
                    for x in range(16):
                        sprite[y, x] = sprite_data[y*16 + x]
                
                self.sprites[i] = sprite
                
                # Also update the sprites_data structure
                row = i // 10
                col = i % 10
                if row < 10 and col < 10:  # Ensure we don't exceed array bounds
                    self.sprites_data[row][col].shp = sprite
            
            print(f"Loaded {sprite_count} sprites from {file_path}")
            return True
        except Exception as e:
            print(f"Error loading STD file: {e}")
            return False
    
    def load_inf_file(self, file_path):
        """Load a .inf file containing sprite metadata"""
        try:
            with open(file_path, "rb") as f:
                # The inf file format has max counts for each row, followed by sprite data
                for row in range(10):
                    # Read the max count for this row
                    max_count_str = f.readline().strip()
                    if not max_count_str:
                        break
                    
                    max_count = int(max_count_str)
                    self.anim_objects[row].max = max_count
                    
                    # Read data for each sprite in this row (up to max_count)
                    for s in range(max_count + 1):  # Including the last one
                        # Based on the C code, we need to read:
                        # int w, h, n, c, flag, rowflag
                        # char shp[260]
                        # But shape data is already loaded from .std, so we skip the shape bytes
                        shape_header = f.read(16)  # Read the first 16 bytes (header)
                        
                        if len(shape_header) < 16:
                            print(f"Warning: Incomplete data for shape {s} in row {row}")
                            break
                        
                        # Parse the header
                        # Format could be different, we're assuming ints are 4 bytes each
                        if s < 10:  # Ensure we don't exceed array bounds
                            shape = self.sprites_data[row][s]
                            shape.w, shape.h, shape.n, shape.c = struct.unpack("<iiii", shape_header[:16])
                            
                            # Read flag and rowflag
                            flag_data = f.read(8)
                            if len(flag_data) == 8:
                                shape.flag, shape.rowflag = struct.unpack("<ii", flag_data)
                            
                            # Skip shape data - We already have it from .std
                            f.seek(256, os.SEEK_CUR)
                
            print(f"Loaded shape metadata from {file_path}")
            return True
        except Exception as e:
            print(f"Error loading INF file: {e}")
            return False
    
    def load_map_file(self, file_path):
        """Load a .map file containing layout data"""
        try:
            with open(file_path, "rb") as f:
                for i in range(100):
                    for j in range(100):
                        line = f.readline().strip()
                        if not line:
                            break
                        self.layout[j][i] = int(line)
            
            print(f"Loaded layout data from {file_path}")
            return True
        except Exception as e:
            print(f"Error loading MAP file: {e}")
            return False
    
    def load_dat_file(self, file_path):
        """Load a .dat file containing animation object data"""
        try:
            with open(file_path, "rb") as f:
                # Try to read the animobjects structure
                # This is complex and we're making assumptions about structure size and alignment
                data = f.read()
                
                # For now, we'll just read the data but not do much with it
                # since we already have the necessary data from other files
                
            print(f"Loaded animation data from {file_path}")
            return True
        except Exception as e:
            print(f"Error loading DAT file: {e}")
            return False
    
    def draw_sprite(self, row, index):
        """Draw a single sprite at the specified row and index"""
        if row < 0 or row >= 10 or index < 0 or index >= 10:
            return
            
        sprite = self.sprites_data[row][index].shp
        sprite_surface = pygame.Surface((16*self.zoom, 16*self.zoom))
        sprite_surface.fill((50, 50, 50))  # Gray background
        
        # Draw each pixel of the sprite, scaled up
        for y in range(16):
            for x in range(16):
                color_index = int(sprite[y, x])
                if 0 <= color_index < len(self.palette):
                    color = self.palette[color_index]
                    pygame.draw.rect(
                        sprite_surface, 
                        color, 
                        (x*self.zoom, y*self.zoom, self.zoom, self.zoom)
                    )
        
        # Center the sprite on screen
        sprite_rect = sprite_surface.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
        self.screen.blit(sprite_surface, sprite_rect)
        
        # Draw the grid
        for y in range(17):
            pygame.draw.line(
                sprite_surface,
                (100, 100, 100),
                (0, y*self.zoom),
                (16*self.zoom, y*self.zoom),
                1
            )
        
        for x in range(17):
            pygame.draw.line(
                sprite_surface,
                (100, 100, 100),
                (x*self.zoom, 0),
                (x*self.zoom, 16*self.zoom),
                1
            )
        
        self.screen.blit(sprite_surface, sprite_rect)
        
    def draw_sprite_grid(self):
        """Draw all sprites in a grid"""
        grid_width = 16 * self.zoom * self.grid_cols
        grid_height = 16 * self.zoom * self.grid_rows
        grid_surface = pygame.Surface((grid_width, grid_height))
        grid_surface.fill((50, 50, 50))  # Gray background
        
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                if row >= 10 or col >= 10:  # Bounds check
                    continue
                    
                sprite = self.sprites_data[row][col].shp
                flag = self.sprites_data[row][col].flag
                
                # Only draw sprites that have their flag set (if we're being strict)
                # if flag == 0:
                #     continue
                
                # Draw each pixel of the sprite
                for y in range(16):
                    for x in range(16):
                        color_index = int(sprite[y, x])
                        if 0 <= color_index < len(self.palette):
                            color = self.palette[color_index]
                            pygame.draw.rect(
                                grid_surface, 
                                color, 
                                (col*16*self.zoom + x*self.zoom, 
                                 row*16*self.zoom + y*self.zoom, 
                                 self.zoom, self.zoom)
                            )
                
                # Draw sprite border (red for active, gray for inactive)
                border_color = (255, 0, 0) if flag != 0 else (100, 100, 100)
                pygame.draw.rect(
                    grid_surface,
                    border_color,
                    (col*16*self.zoom, row*16*self.zoom, 16*self.zoom, 16*self.zoom),
                    1
                )
                
                # Draw sprite index
                index_text = self.font.render(f"{row*10+col}", True, (200, 200, 200))
                grid_surface.blit(index_text, (col*16*self.zoom + 2, row*16*self.zoom + 2))
        
        # Center the grid on screen
        grid_rect = grid_surface.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
        self.screen.blit(grid_surface, grid_rect)
    
    def draw_layout(self, x_offset=0, y_offset=0):
        """Draw the layout view from the .map file"""
        visible_width = min(20, 100 - x_offset)
        visible_height = min(15, 100 - y_offset)
        
        layout_width = visible_width * 16 * self.zoom
        layout_height = visible_height * 16 * self.zoom
        
        layout_surface = pygame.Surface((layout_width, layout_height))
        layout_surface.fill((40, 40, 40))  # Dark gray background
        
        for y in range(visible_height):
            for x in range(visible_width):
                map_value = self.layout[x + x_offset][y + y_offset]
                
                if map_value >= 0:
                    # Extract row and sprite index from map value
                    row = map_value // 10
                    sprite_idx = map_value % 10
                    
                    if row < 10 and sprite_idx < 10:  # Bounds check
                        sprite = self.sprites_data[row][sprite_idx].shp
                        
                        # Draw the sprite
                        for sy in range(16):
                            for sx in range(16):
                                color_index = int(sprite[sy][sx])
                                if color_index > 0 and color_index < len(self.palette):  # Skip transparent (0)
                                    color = self.palette[color_index]
                                    pygame.draw.rect(
                                        layout_surface,
                                        color,
                                        (x*16*self.zoom + sx*self.zoom,
                                         y*16*self.zoom + sy*self.zoom,
                                         self.zoom, self.zoom)
                                    )
        
        # Draw grid lines
        for y in range(visible_height + 1):
            pygame.draw.line(
                layout_surface,
                (60, 60, 60),
                (0, y*16*self.zoom),
                (layout_width, y*16*self.zoom),
                1
            )
        
        for x in range(visible_width + 1):
            pygame.draw.line(
                layout_surface,
                (60, 60, 60),
                (x*16*self.zoom, 0),
                (x*16*self.zoom, layout_height),
                1
            )
        
        # Center the layout on screen
        layout_rect = layout_surface.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
        self.screen.blit(layout_surface, layout_rect)
        
    def draw_info(self):
        """Draw information about the current sprite and controls"""
        if self.current_file_base:
            # File info
            file_info = f"File: {self.current_file_base}"
            file_text = self.font.render(file_info, True, (255, 255, 255))
            self.screen.blit(file_text, (10, 10))
            
            # Mode info
            mode_info = f"Mode: {self.view_mode.capitalize()}"
            mode_text = self.font.render(mode_info, True, (255, 255, 255))
            self.screen.blit(mode_text, (10, 30))
            
            # Sprite/Row info
            if self.view_mode == "sprite":
                sprite_info = f"Row: {self.current_row}, Sprite: {self.current_sprite_index} " + \
                              f"(Flag: {self.sprites_data[self.current_row][self.current_sprite_index].flag})"
                sprite_text = self.font.render(sprite_info, True, (255, 255, 255))
                self.screen.blit(sprite_text, (10, 50))
            
            # Help text
            help_texts = [
                "Left/Right: Change sprite",
                "Up/Down: Change row",
                "PgUp/PgDn: Change file",
                "Tab: Cycle view modes (sprite/grid/layout)",
                "+/-: Zoom in/out",
                "L: Load another file",
                "Esc: Quit"
            ]
            
            y_pos = self.screen.get_height() - len(help_texts) * 20 - 10
            for text in help_texts:
                rendered_text = self.font.render(text, True, (200, 200, 200))
                self.screen.blit(rendered_text, (10, y_pos))
                y_pos += 20
    
    def prompt_for_file(self):
        """Prompt the user to enter a file basename"""
        pygame.draw.rect(self.screen, (0, 0, 0), (100, 300, 824, 100))
        pygame.draw.rect(self.screen, (100, 100, 100), (100, 300, 824, 100), 2)
        
        prompt_text = self.font.render("Enter file basename (without extension):", True, (255, 255, 255))
        self.screen.blit(prompt_text, (120, 320))
        
        pygame.display.flip()
        
        input_text = ""
        input_active = True
        
        while input_active:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return None
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        input_active = False
                    elif event.key == K_ESCAPE:
                        return None
                    elif event.key == K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode
            
            # Clear the input area
            pygame.draw.rect(self.screen, (0, 0, 0), (120, 350, 784, 30))
            
            # Render the current input text
            input_surface = self.font.render(input_text, True, (255, 255, 255))
            self.screen.blit(input_surface, (120, 350))
            
            pygame.display.flip()
            self.clock.tick(30)
        
        return input_text
                    
    def run(self):
        """Main application loop"""
        if not self.scan_directory():
            print("No .std files found in the directory")
            return
            
        if self.std_files:
            self.load_file_set(self.std_files[0].stem)
            
        layout_x_offset = 0
        layout_y_offset = 0
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    elif event.key == K_TAB:
                        # Cycle view modes
                        if self.view_mode == "sprite":
                            self.view_mode = "grid"
                        elif self.view_mode == "grid":
                            self.view_mode = "layout"
                        else:
                            self.view_mode = "sprite"
                    elif event.key == K_l:
                        # Load another file
                        filename = self.prompt_for_file()
                        if filename:
                            self.load_file_set(filename)
                    elif event.key == K_RIGHT:
                        if self.view_mode == "sprite":
                            self.current_sprite_index = (self.current_sprite_index + 1) % 10
                        elif self.view_mode == "layout":
                            layout_x_offset = min(layout_x_offset + 1, 80)
                    elif event.key == K_LEFT:
                        if self.view_mode == "sprite":
                            self.current_sprite_index = (self.current_sprite_index - 1) % 10
                        elif self.view_mode == "layout":
                            layout_x_offset = max(layout_x_offset - 1, 0)
                    elif event.key == K_DOWN:
                        if self.view_mode == "sprite":
                            self.current_row = (self.current_row + 1) % 10
                        elif self.view_mode == "layout":
                            layout_y_offset = min(layout_y_offset + 1, 85)
                    elif event.key == K_UP:
                        if self.view_mode == "sprite":
                            self.current_row = (self.current_row - 1) % 10
                        elif self.view_mode == "layout":
                            layout_y_offset = max(layout_y_offset - 1, 0)
                    elif event.key == K_PAGEUP:
                        # Go to previous file
                        if self.std_files:
                            file_index = self.base_filenames.index(self.current_file_base) if self.current_file_base in self.base_filenames else 0
                            new_index = (file_index - 1) % len(self.base_filenames)
                            self.load_file_set(self.base_filenames[new_index])
                    elif event.key == K_PAGEDOWN:
                        # Go to next file
                        if self.std_files:
                            file_index = self.base_filenames.index(self.current_file_base) if self.current_file_base in self.base_filenames else 0
                            new_index = (file_index + 1) % len(self.base_filenames)
                            self.load_file_set(self.base_filenames[new_index])
                    elif event.key in (K_PLUS, K_EQUALS):
                        # Zoom in
                        self.zoom = min(16, self.zoom + 1)
                    elif event.key == K_MINUS:
                        # Zoom out
                        self.zoom = max(1, self.zoom - 1)
                        
            # Draw background
            self.screen.fill((30, 30, 30))
            
            # Draw content based on view mode
            if self.view_mode == "sprite":
                self.draw_sprite(self.current_row, self.current_sprite_index)
            elif self.view_mode == "grid":
                self.draw_sprite_grid()
            elif self.view_mode == "layout":
                self.draw_layout(layout_x_offset, layout_y_offset)
                
            # Draw information
            self.draw_info()
            
            pygame.display.flip()
            self.clock.tick(30)
            
        pygame.quit()
        
if __name__ == "__main__":
    # Use command line argument for directory if provided, otherwise use current directory
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    viewer = DOSSpriteViewer(directory)
    viewer.run()
