#include "unistd.h"
#include "time.h"
#include "stdio.h"
#include "libpruio/pruio.h"
#include "libpruio/pruio_pins.h"

#define PIN P8_07               //!< pin to use for GPIO trigger
#define MODE PRUIO_GPIO_IN_1      //!< which pinmode to use

int main (int argc, char **argv){
  const uint32 tSamp = (uint32) atoi(argv[1]);  //!< The number of samples in the files (per step).
  const uint32 tmr = (uint32) atoi(argv[2]);    //!< The sampling rate in ns (20000 -> 50 kHz).
  const uint32 NoStep = 2;                      //!< The number of active steps (must match setStep calls and mask).
  const uint32 NoFile = 1;                      //!< The number of files to write.
  const char *NamFil = "output2.%u";  
  struct timespec mSec;
  mSec.tv_nsec = 1000000;
  
  pruIo *io = pruio_new(PRUIO_ACT_ADC+PRUIO_ACT_FREMUX, 0, 0, 0);
  if (io->Errr){
    printf("constructor failed (%s)\n", io->Errr);
    return 1;
  }
  printf("pruio constructor\n");
  do{
    //Set-up GPIO on P8_07
    if (pruio_gpio_config(io, PIN, MODE)){
      printf("GPIO configuration failed: (%s)\n", io->Errr);
      break;
    }
    printf("gpio config\n");
    //Set-up the AIN-1 channel
    if (pruio_adc_setStep(io, 10, 1, 0, 0, 0)){
      printf("step10 configuration failed: (%s)\n", io->Errr);
      break;
    }
    //Set-up the AIN-2 channel
    if (pruio_adc_setStep(io, 11, 2, 0, 0, 0)){
      printf("step 11 configuration failed: (%s)\n", io->Errr);
      break;
    }
    printf("adc step\n");
    
    //Define bit mask for ADC channels
    uint32 mask = 6 << 9;                          //!< The active steps (10 to 11) (6<<9 -> 0000110000000000)
    uint32 tInd = tSamp * NoStep;
    uint32 half = ((io->ESize >> 2) / NoStep) * NoStep;   //!< The maximum index of the half ring buffer
    
    if (half > tInd){                             //!< adapt size for small files
      half = tInd;
    }
    uint32 samp = (half << 1) / NoStep;           //!< Number of samples (per step)
    
    if (pruio_config(io, samp, mask, tmr, 0)){    //!< configure driver
      printf("config failed: (%s)\n", io->Errr);
      break;
    }
    printf("pruio config\n");
    
    //Set-up GPIO trigger
    uint32 trg = pruio_adc_mm_trg_pin(io, PIN, 0, 0); //! 3rd input is value to check (1=HI, 0=LO), 4th input is delay number
    if (trg == 0){
      printf("trigger config failed: (%s)\n", io->Errr);
      break;
    }
    printf("%d\n",trg);
    
    uint32 gpio_val = pruio_gpio_Value(io, PIN);
    printf("gpio state: (%d)\n",gpio_val);
    //Start measurement in MM mode
    if (pruio_mm_start(io, trg, 0, 0, 0)){
      printf("mm_start failed (%s)\n", io->Errr);
      break;
    }
    
    uint16 *p0 = io->Adc->Value;  //!< A pointer to the start of the ring buffer.
    uint16 *p1 = p0 + half;       //!< A pointer to the middle of the ring buffer.
    uint32 n;  //!< File counter.
    char fName[20];
    for(n = 0; n < NoFile; n++){
      sprintf(fName, NamFil, n);
      printf("Creating file %s\n", fName);
      FILE *oFile = fopen(fName, "w");
      uint32 i = 0;               //!< Start index.
      while(i < tInd){
        i += half;
        if(i > tInd){         // fetch the rest(maybe no complete chunk)
          uint32 rest = tInd + half - i;
          uint32 iEnd = p1 >= p0 ? rest : rest + half;
          while(io->DRam[0] < iEnd) nanosleep(&mSec, NULL);
          printf("  writing samples %u-%u\n", tInd -rest, tInd-1);
          fwrite(p0, sizeof(uint16), rest, oFile);
          uint16 *swap = p0;
          p0 = p1;
          p1 = swap;
          break;
        }
        if(p1 > p0) while(io->DRam[0] < half) nanosleep(&mSec, NULL);
        else        while(io->DRam[0] > half) nanosleep(&mSec, NULL);
        printf("  writing samples %u-%u\n", i-half, i-1);
        fwrite(p0,  sizeof(uint16), half, oFile);
        uint16 *swap = p0;
        p0 = p1;
        p1 = swap;
      }
      fclose(oFile);
      printf("Finished file %s\n", fName);
    }
  } while(0);
  printf("end\n");
  pruio_destroy(io);
  return 0;
}
