#include <SDL2/SDL.h>
#include <stdio.h>
#include <stdbool.h>

#define REMOVEGAMERESOURCE(t) if(t!=NULL){SDL_DestroyTexture(t);}
#define REMOVESURFACE(s) if(s!=NULL){SDL_FreeSurface(s);}

SDL_Surface* images[100];
char temp2[37];
int count=0;

///////////////////////////////////////////////////////////
void Load_STD_File(char* filename);
///////////////////////////////////////////////////////////

int main(int args, char* argv[])
{
    if (args < 3)
    {
        SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_INFORMATION, "STDCNV.EXE", 
            "use: STDCNV.EXE STDFILE SAVEDIR\nProgrammed by Franco Gaetan", NULL);
        return -1;
    }

    // Initialize SDL
    if (SDL_Init(SDL_INIT_VIDEO) < 0)
    {
        printf("SDL could not initialize! SDL_Error: %s\n", SDL_GetError());
        return -1;
    }

    // Create window
    sprintf(temp2, "STDCNV.EXE -> [%s] : Press ESC to quit", argv[1]);
    SDL_Window* window = SDL_CreateWindow(temp2, 
                                        SDL_WINDOWPOS_UNDEFINED, 
                                        SDL_WINDOWPOS_UNDEFINED, 
                                        640, 480, 
                                        SDL_WINDOW_SHOWN);
    if (window == NULL)
    {
        printf("Window could not be created! SDL_Error: %s\n", SDL_GetError());
        SDL_Quit();
        return -1;
    }

    // Create renderer
    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    if (renderer == NULL)
    {
        printf("Renderer could not be created! SDL_Error: %s\n", SDL_GetError());
        SDL_DestroyWindow(window);
        SDL_Quit();
        return -1;
    }
    
    // Initialize all surfaces
    for (int index = 0; index < 100; index++)
    {
        images[index] = SDL_CreateRGBSurface(0, 16, 16, 32, 
                                          0xFF000000, 
                                          0x00FF0000, 
                                          0x0000FF00, 
                                          0x000000FF);
    }
    
    // Load STD file
    Load_STD_File(argv[1]);
    
    // Display sprites on screen
    SDL_Texture* textures[100];
    SDL_Rect sourceRect = {0, 0, 16, 16};
    SDL_Rect destRect = {0, 0, 32, 32};
    
    // Clear the screen
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
    SDL_RenderClear(renderer);
    
    // Create textures and render them
    for (int y = 0; y < 10; y++)
    {
        for (int x = 0; x < 10; x++)
        {
            int index = x + y * 10;
            textures[index] = SDL_CreateTextureFromSurface(renderer, images[index]);
            
            destRect.x = x * 32;
            destRect.y = y * 32;
            
            SDL_RenderCopy(renderer, textures[index], &sourceRect, &destRect);
        }
    }
    
    // Update the screen
    SDL_RenderPresent(renderer);
    
    // Save all bitmaps
    for (int iindex = 0; iindex < 100; iindex++)
    {
        char temp[256];
        sprintf(temp, "%s/%s_%d.bmp", argv[2], argv[2], iindex);
        int result = SDL_SaveBMP(images[iindex], temp);
        if (result != 0)
        {
            char errorMsg[512];
            sprintf(errorMsg, "Error saving bitmap #%d to %s/%s_%d.bmp: %s", 
                    iindex, argv[2], argv[2], iindex, SDL_GetError());
            SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_ERROR, "Save Error", errorMsg, window);
        }
        else
        {
            count++;
        }
    }
    
    // Show success message
    char successMsg[256];
    sprintf(successMsg, "Saved %d bitmaps in %s", count, argv[2]);
    SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_INFORMATION, "Success", successMsg, window);
    
    // Wait for ESC key
    SDL_Event e;
    bool quit = false;
    while (!quit)
    {
        while (SDL_PollEvent(&e) != 0)
        {
            if (e.type == SDL_QUIT)
            {
                quit = true;
            }
            else if (e.type == SDL_KEYDOWN)
            {
                if (e.key.keysym.sym == SDLK_ESCAPE)
                {
                    quit = true;
                }
            }
        }
    }
    
    // Cleanup resources
    for (int i = 0; i < 100; i++)
    {
        REMOVEGAMERESOURCE(textures[i]);
        REMOVESURFACE(images[i]);
    }
    
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    
    return 0;
}

///////////////////////////////////////////////////////////
void Load_STD_File(char* filename)
{
    FILE* fp = fopen(filename, "rb");
    if (fp == NULL)
    {
        printf("Failed to open file: %s\n", filename);
        return;
    }
    
    int sprite_index = 0, x = 0, y = 0;
    
    for (sprite_index = 0; sprite_index < 100; sprite_index++)
    {
        for (y = 0; y < 16; y++)
        {
            for (x = 0; x < 16; x++)
            {
                // Get pixel value from file
                Uint8 colorIndex = getc(fp);
                
                // We need to lock the surface before accessing pixels directly
                SDL_LockSurface(images[sprite_index]);
                
                // Calculate pixel position
                Uint32* pixels = (Uint32*)images[sprite_index]->pixels;
                int pixelPos = y * images[sprite_index]->w + x;
                
                // Set pixel value (assuming a simple palette conversion)
                // This needs to be adjusted based on actual color needs
                Uint32 r = colorIndex;
                Uint32 g = colorIndex;
                Uint32 b = colorIndex;
                Uint32 color = (r << 24) | (g << 16) | (b << 8) | 0xFF;
                
                pixels[pixelPos] = color;
                
                // Unlock the surface
                SDL_UnlockSurface(images[sprite_index]);
            }
        }
    }
    
    fclose(fp);
}
///////////////////////////////////////////////////////////
// end of file
