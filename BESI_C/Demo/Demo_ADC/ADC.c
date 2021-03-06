/* 
Based on code from https://github.com/VegetableAvenger
measures audio at 10KHz with Mic connected to AIN1 pin on BBB
output is the sum of the differences between each sample and 
OFFSET over SAMPLE_WINDOW
Usage: ./ADC <Start Time>

*/
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "../../BBBio_lib/BBBiolib.h"
/* ----------------------------------------------------------- */
#define BUFFER_SIZE 10000
#define TEMP_BUFFER_SIZE 10
#define SAMPLE_SIZE 10000
#define TEMP_SAMPLE_SIZE 10
#define SAMPLE_WINDOW 100
#define OFFSET 0.86
#define TIMESTEP (float)SAMPLE_WINDOW/10000
/* ----------------------------------------------------------- */
int main(int argc, const char* argv[])
{
	unsigned int sample, temp_sample;
	int i ,j, k;
	unsigned int buffer_AIN_1[BUFFER_SIZE] = {0};
	unsigned int buffer_AIN_0[TEMP_BUFFER_SIZE] = {0};
	FILE *adc_file;
	FILE *temp_file;
	struct timeval t_start, t_end;
 	float mTime =0;
 	float avg;

	/* BBBIOlib init*/
	iolib_init();

	/* using ADC_CALC toolkit to decide the ADC module argument . Example Sample rate : 10000 sample/s
	 *
	 *	#./ADC_CALC -f 10000 -t 5
	 *
	 *	Suggest Solution :
	 *		Clock Divider : 160 ,   Open Dly : 0 ,  Sample Average : 1 ,    Sample Dly : 1
	 *
	 */
//	const int clk_div = 34 ;
	const int clk_div = 160;
	const int open_dly = 0;
	const int sample_dly = 1;
	
	//adc_file = fopen("adc_voice.txt", "w");
	//temp_file = fopen("temp.txt", "a");
	
	//fprintf(adc_file, "%s\n", argv[1]);
	//fprintf(temp_file, "%s\n", argv[1]);
	//fclose(temp_file);

	/*ADC work mode : Timer interrupt mode
	 *	Note : This mode handle SIGALRM using signale() function in BBBIO_ADCTSC_work();
	 */
	BBBIO_ADCTSC_module_ctrl(BBBIO_ADC_WORK_MODE_TIMER_INT, clk_div);

	BBBIO_ADCTSC_channel_ctrl(BBBIO_ADC_AIN1, BBBIO_ADC_STEP_MODE_SW_CONTINUOUS, open_dly, sample_dly, \
				BBBIO_ADC_STEP_AVG_1, buffer_AIN_1, BUFFER_SIZE);
	BBBIO_ADCTSC_channel_ctrl(BBBIO_ADC_AIN0, BBBIO_ADC_STEP_MODE_SW_CONTINUOUS, open_dly, sample_dly, \
				BBBIO_ADC_STEP_AVG_1, buffer_AIN_0, TEMP_BUFFER_SIZE);
	
	gettimeofday(&t_start, NULL);

	i = 0;
		BBBIO_ADCTSC_channel_enable(BBBIO_ADC_AIN1);
		BBBIO_ADCTSC_channel_disable(BBBIO_ADC_AIN0);
		BBBIO_ADCTSC_work(SAMPLE_SIZE);

		avg = 0;
		for(j = 0 ; j < SAMPLE_SIZE ; j++) {
			sample = buffer_AIN_1[j];
			avg += fabs(OFFSET - ((float)sample / 4095.0f) * 1.8f);
			
			if (((j + 1) % SAMPLE_WINDOW) == 0){
				//fprintf(adc_file, "%0.3f,%0.2f\n", mTime + TIMESTEP * (float)i, avg);
				printf("%0.3f,%0.2f,", mTime + TIMESTEP * (float)i, avg);
				avg = 0;
				i++;
			}
        }
        BBBIO_ADCTSC_channel_enable(BBBIO_ADC_AIN0);
        BBBIO_ADCTSC_channel_disable(BBBIO_ADC_AIN1);
        BBBIO_ADCTSC_work(TEMP_SAMPLE_SIZE);
        sample = buffer_AIN_0[0];
        gettimeofday(&t_end, NULL);
		mTime = (t_end.tv_sec -t_start.tv_sec)*1000000.0 +(t_end.tv_usec -t_start.tv_usec);
		mTime /=1000000.0f;
		//temp_file = fopen("temp.txt", "a");
		//printf("temp: %0.3f\n", ((float)sample / 4095.0f) * 1.8f);
		//fprintf(temp_file, "%0.3f,%0.4f\n", mTime, ((float)sample / 4095.0f) * 1.8f);
		printf("%0.3f,%0.4f", mTime, ((float)sample / 4095.0f) * 1.8f);
		//fclose(temp_file);
        i=0;
	
	iolib_free();
	//fclose(adc_file);
	return 0;
}


