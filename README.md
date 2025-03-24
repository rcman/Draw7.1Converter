# Draw7.1Converter
This is a converter which takes the raw file from my draw program and makes them in to BMP files

The saved filed from the draw program are saved with extension .std

The converter works by saving the STD file in the desination name or your choice. The desination name must also be the directory name. 

Example

stdconv sample1.std  myname

there must be a directory called myname

Download the VMDK files here

https://www.dropbox.com/s/4jd50b8hfv4v3hf/MS-DOS%206.22-s001.zip?dl=0
<br>

# SDL2 Version

<br>

Library Changes:

Replaced Allegro headers with SDL2/SDL.h
Added stdbool.h for boolean support


Graphics Handling:

Switched from Allegro's BITMAP to SDL2's Surface and Texture objects
Updated the window and rendering initialization process
Implemented proper SDL2 renderer for displaying sprites


Event Handling:

Replaced Allegro's key array with SDL2's event polling system
Added proper event loop to handle keyboard input and window events


Resource Management:

Updated the resource cleanup macro for SDL textures and surfaces
Added proper cleanup for all SDL resources


File Handling:

Adapted the pixel access method to work with SDL surfaces
Implemented SDL_LockSurface/SDL_UnlockSurface for direct pixel manipulation


User Interface:

Replaced allegro_message with SDL_ShowSimpleMessageBox
Added better error reporting with SDL_GetError()
