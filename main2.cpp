///////////////////////////////////////////////////////////
// STDCNV.EXE - F.G. GCDraw Spriteset Converter            
// Programmed by Richard Marks                             
// © Copyright 2004, CCPS Solutions.                       
// http://ccps.rpgdx.net                                   
///////////////////////////////////////////////////////////
#include <allegro.h>
#include <stdio.h>

#define REMOVEGAMERESOURCE(b) if(b!=NULL){destroy_bitmap(b);}
BITMAP* images[100];
char temp2[37];
int count=0;
///////////////////////////////////////////////////////////
void Load_STD_File (char* filename);

///////////////////////////////////////////////////////////

int main (int args, char* argv[])
{
 allegro_init(); 
 install_timer();
 install_keyboard();
 set_gfx_mode(GFX_AUTODETECT_WINDOWED, 640, 480, 0, 0);

 if (args < 3)
 {
  allegro_message("use: STDCNV.EXE STDFILE SAVEDIR\nProgrammed by Richard Marks - 9:04 PM 11-15-04");
  return -1;
 }
 
 sprintf(temp2, "STDCNV.EXE -> [%s] : Press ESC to quit", argv[1]);
 set_window_title(temp2);


 for (int index = 0; index < 100; index++)
 {
  images[index] = create_bitmap (16, 16);
 } 
 Load_STD_File (argv[1]);

 for (int y = 0; y < 10; y++)
 {
  for (int x = 0; x < 10; x++)
  {
   stretch_blit(images[x+y*10],screen,0,0,16,16,x*32,y*32,32,32);
  }
 }
 for (int iindex=0; iindex<100; iindex++)
 {
  char temp[20];
  sprintf(temp,"%s/%s_%d.bmp", argv[2], argv[2], iindex);
  int result = save_bitmap (temp, images[iindex], NULL);
  if (result!=0)
  {
   allegro_message("error saving bitmap #%d to %s/%s_%d.bmp", iindex, argv[2], argv[2],  iindex);
  }
  else
  {
   count++;
  }
 }
 allegro_message("saved %d bitmaps in %s",count, argv[2]);
 while(!key[KEY_ESC]);
 
 for (int i = 0; i < 100; i++)
  REMOVEGAMERESOURCE(images[i])
 return 0;
}
END_OF_MAIN()

///////////////////////////////////////////////////////////

void Load_STD_File (char* filename)
{
 FILE* fp = fopen (filename, "rb");
 int sprite_index=0, x=0, y=0;
 for (sprite_index = 0; sprite_index < 100; sprite_index++)
 {
  for (y = 0; y < 16; y++)
  {
   for (x = 0; x < 16; x++)
   {
    images[sprite_index]->line[y][x] = getc(fp);
   }
  }
 }
 fclose (fp);
}

///////////////////////////////////////////////////////////
// end of file

