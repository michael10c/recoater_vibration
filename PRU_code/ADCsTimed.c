/** \file rb_file.c
\brief Example: fetch ADC samples in a ring buffer and save to file.
This file contains an example on how to use the ring buffer mode of
libpruio. A fixed step mask of AIN-0, AIN-1 and AIN-2 get configured
for maximum speed, sampled in to the ring buffer and from there saved
as raw data to some files. Find a functional description in section
\ref sSecExaRbFile.
Licence: GPLv3, Copyright 2014-\Year by \Mail
Thanks for C code translation: Nils Kohrs <nils.kohrs@gmail.com>
Compile by: `gcc -Wall -o rb_file rb_file.c -lpruio`
\since 0.4.0
*/

#include "unistd.h"
#include "time.h"
#include "stdio.h"
#include "libpruio/pruio.h"
#ifdef __unix__
# include <unistd.h>
#elif defined _WIN32
# include <windows.h>
#define sleep(x) Sleep(1000 * (x))
#endif

//! The main function.
int main(int argc, char **argv)
{
  time_t begin = time(NULL);
  const uint32 tSamp = (uint32) atoi(argv[1]);  //!< The number of samples in the files (per step).
  const uint32 tmr = (uint32) atoi(argv[2]);     //!< The sampling rate in ns (20000 -> 50 kHz).
  const uint32 NoStep = 2;      //!< The number of active steps (must match setStep calls and mask).
  const uint32 NoFile = 2;      //!< The number of files to write.
  const char *NamFil = "output2.%u";

  struct timespec mSec;
  mSec.tv_nsec = 1000000;
  time_t end1 = time(NULL);
  printf("The elapsed time for variable initialization is %d seconds\n", (end1 - begin));

  pruIo *io = pruio_new(PRUIO_ACT_ADC+PRUIO_ACT_FREMUX, 0, 0, 0); //! create new driver
  time_t end2 = time(NULL);
  printf("The elapsed time for driver creation is %d seconds\n", (end2 - end1));
  if (io->Errr){
               printf("constructor failed (%s)\n", io->Errr); return 1;}

  do {
    //Set-up the AIN-1 channel
    if (pruio_adc_setStep(io, 10, 1, 0, 0, 0)){ //          step 10, AIN-1
        printf("step 10 configuration failed: (%s)\n", io->Errr);break;}
    time_t end3 = time(NULL);
    printf("The elapsed time for AIN1 channel setup is %d seconds\n", (end3 - end2));
    //Set-up the AIN-2 channel
    if (pruio_adc_setStep(io,11, 2, 0, 0, 0)){ //         step 11, AIN-2
       printf("step 11 configuration failed: (%s)\n", io->Errr); break;}
    time_t end4 = time(NULL);
    printf("The elapsed time for AIN2 channel setup is %d seconds\n", (end4 - end3));

    //Define bit mask for the ADC channels (AIN-1 and AIN-2)
    uint32 mask = 6 << 9;         //!< The active steps (10 to 11) (6<<9 --> 0000110000000000)

    uint32 tInd = tSamp * NoStep; //!< The maximum total index.
    uint32 half = ((io->ESize >> 2) / NoStep) * NoStep; //!< The maximum index of the half ring buffer.

    if (half > tInd){ half = tInd;}  //       adapt size for small files
    uint32 samp = (half << 1) / NoStep; //!< The number of samples (per step).
    time_t end5 = time(NULL);
    printf("The elapsed time for defining the ADC channels bit mask is %d seconds\n", (end5 - end4));

    if (pruio_config(io, samp, mask, tmr, 0)){ //       configure driver
                       printf("config failed (%s)\n", io->Errr); break;}

    if (pruio_rb_start(io)){
                     printf("rb_start failed (%s)\n", io->Errr); break;}
    time_t end6 = time(NULL);
    printf("The elapsed time for configuring the driver and starting the ring buffer mode is %d seconds\n", (end6 - end5));

    uint16 *p0 = io->Adc->Value;  //!< A pointer to the start of the ring buffer.
    uint16 *p1 = p0 + half;       //!< A pointer to the middle of the ring buffer.
    uint32 n;  //!< File counter.
    char fName[20];
    for(n = 0; n < NoFile; n++){
      sprintf(fName, NamFil, n);
      //printf("Creating file %s\n", fName);
      FILE *oFile = fopen(fName, "w");
      uint32 i = 0;               //!< Start index.
      while(i < tInd){
        i += half;
        if(i > tInd){         // fetch the rest(maybe no complete chunk)
          uint32 rest = tInd + half - i;
          uint32 iEnd = p1 >= p0 ? rest : rest + half;
          while(io->DRam[0] < iEnd) nanosleep(&mSec, NULL);
          //printf("  writing samples %u-%u\n", tInd -rest, tInd-1);
          fwrite(p0, sizeof(uint16), rest, oFile);
          uint16 *swap = p0;
          p0 = p1;
          p1 = swap;
          break;
        }
        if(p1 > p0) while(io->DRam[0] < half) nanosleep(&mSec, NULL);
        else        while(io->DRam[0] > half) nanosleep(&mSec, NULL);
        //printf("  writing samples %u-%u\n", i-half, i-1);
        fwrite(p0,  sizeof(uint16), half, oFile);
        uint16 *swap = p0;
        p0 = p1;
        p1 = swap;
      }
      fclose(oFile);
      time_t end7 = time(NULL);
      printf("The elapsed time for reading and writing samples to file is %d seconds\n", (end7 - end6));
      //printf("Finished file %s\n", fName);
    }
  } while(0);
  pruio_destroy(io);
  return 0;
}
