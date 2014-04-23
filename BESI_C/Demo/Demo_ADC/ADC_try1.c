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
#define MIC_BUFFER_SIZE 10000
#define PIR_BUFFER_SIZE 10000
#define TEMP_BUFFER_SIZE 10

#define MIC_SAMPLE_SIZE 10000
#define PIR_SAMPLE_SIZE 10000
#define TEMP_SAMPLE_SIZE 10

#define MIC_OFFSET 0.9
#define PIR1_OFFSET 0
#define PIR2_OFFSET 0

#define SAMPLE_SIZE (MIC_SAMPLE_SIZE>PIR_SAMPLE_SIZE?(int)MIC_SAMPLE_SIZE:(int)PIR_SAMPLE_SIZE)
#define SAMPLE_WINDOW 100
#define TIMESTEP (float)SAMPLE_WINDOW/10000

/* ----------------------------------------------------------- */
float highPassFilter(float last_output, float input, float last_input);

int main(int argc, const char* argv[])
{
	unsigned int mic_sample,pir1_sample,pir2_sample,temp_sample;
	int i ,j, k;
	unsigned int buffer_AIN_1[MIC_BUFFER_SIZE] = {0};
	unsigned int buffer_AIN_2[PIR_BUFFER_SIZE] = {0};
	unsigned int buffer_AIN_3[PIR_BUFFER_SIZE] = {0};
	unsigned int buffer_AIN_0[TEMP_BUFFER_SIZE] = {0};
	FILE *adc_file;
	FILE *temp_file;
	struct timeval t_start, t_end;
 	float mTime =0;
 	float mic_avg, pir1_avg, pir2_avg, mic_out, last_mic_sample, last_mic_output, filter_out;

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
	const int clk_div = 53;
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

	BBBIO_ADCTSC_channel_ctrl(BBBIO_ADC_AIN1, BBBIO_ADC_STEP_MODE_SW_CONTINUOUS,\
		open_dly, sample_dly, BBBIO_ADC_STEP_AVG_1, buffer_AIN_1, MIC_BUFFER_SIZE);
	BBBIO_ADCTSC_channel_ctrl(BBBIO_ADC_AIN2, BBBIO_ADC_STEP_MODE_SW_CONTINUOUS,\
		open_dly, sample_dly, BBBIO_ADC_STEP_AVG_1, buffer_AIN_2, PIR_BUFFER_SIZE);
	BBBIO_ADCTSC_channel_ctrl(BBBIO_ADC_AIN3, BBBIO_ADC_STEP_MODE_SW_CONTINUOUS,\
		open_dly, sample_dly, BBBIO_ADC_STEP_AVG_1, buffer_AIN_3, PIR_BUFFER_SIZE);
	BBBIO_ADCTSC_channel_ctrl(BBBIO_ADC_AIN0, BBBIO_ADC_STEP_MODE_SW_CONTINUOUS,\
		open_dly, sample_dly, BBBIO_ADC_STEP_AVG_1, buffer_AIN_0, TEMP_BUFFER_SIZE);
	
	gettimeofday(&t_start, NULL);

        BBBIO_ADCTSC_channel_enable(BBBIO_ADC_AIN1);
	BBBIO_ADCTSC_channel_enable(BBBIO_ADC_AIN2);
	BBBIO_ADCTSC_channel_enable(BBBIO_ADC_AIN3);
	BBBIO_ADCTSC_channel_disable(BBBIO_ADC_AIN0);
	BBBIO_ADCTSC_work(MIC_SAMPLE_SIZE);

	i = 0; k = 0;
	mic_avg = 0; mic_out = 0; last_mic_sample = 0; last_mic_output = 0;
	pir1_avg = 0; pir2_avg = 0;
	for(j = 0 ; j < (int)SAMPLE_SIZE ; j++) {
		mic_sample = buffer_AIN_1[j];
		mic_out = (MIC_OFFSET - ((float)mic_sample / 4095.0f) * 1.8f);
		filter_out = highPassFilter(last_mic_output, mic_out, last_mic_sample); 
		mic_avg += fabs(filter_out);
		last_mic_sample = mic_out;
		last_mic_output = filter_out;
		if (((j+1) % 10) == 0){
			pir1_sample = buffer_AIN_2[j];
			pir1_avg += fabs(PIR1_OFFSET - ((float)pir1_sample / 4095.0f) * 1.8f);
			pir2_sample = buffer_AIN_3[j];
			pir2_avg += fabs(PIR2_OFFSET - ((float)pir2_sample / 4095.0f) * 1.8f);
			k++;
		}	
		if (((j + 1) % SAMPLE_WINDOW) == 0){
			//fprintf(adc_file, "%0.3f,%0.2f\n", mTime + TIMESTEP * (float)i, avg);
			printf("%0.3f,%0.2f,", mTime + TIMESTEP * (float)i, mic_avg);
			mic_avg = 0;
			if ((k % SAMPLE_WINDOW) == 0){
				//fprintf(adc_file, "%0.3f,%0.2f\n", mTime + TIMESTEP * (float)i, avg);
				printf("%0.3f,%0.2f,%0.3f,%0.2f,", mTime + TIMESTEP * (float)i, pir1_avg,  mTime + TIMESTEP * (float)i, pir2_avg);
				pir1_avg = 0; pir2_avg = 0;
			}
			else{
				printf("");
			}
			i++;
		}
       	}

        BBBIO_ADCTSC_channel_disable(BBBIO_ADC_AIN1);
    	BBBIO_ADCTSC_channel_disable(BBBIO_ADC_AIN2);
    	BBBIO_ADCTSC_channel_disable(BBBIO_ADC_AIN3);


	BBBIO_ADCTSC_channel_enable(BBBIO_ADC_AIN0);
	BBBIO_ADCTSC_work(TEMP_SAMPLE_SIZE);
        temp_sample = buffer_AIN_0[0];

        gettimeofday(&t_end, NULL);
	mTime = (t_end.tv_sec -t_start.tv_sec)*1000000.0 +(t_end.tv_usec -t_start.tv_usec);
	mTime /=1000000.0f;
	//temp_file = fopen("temp.txt", "a");
	//printf("temp: %0.3f\n", ((float)sample / 4095.0f) * 1.8f);
	//fprintf(temp_file, "%0.3f,%0.4f\n", mTime, ((float)sample / 4095.0f) * 1.8f);
	printf("%0.3f,%0.4f", mTime, ((float)temp_sample / 4095.0f) * 1.8f);
	//fclose(temp_file);
	BBBIO_ADCTSC_channel_disable(BBBIO_ADC_AIN0);

	iolib_free();
	//fclose(adc_file);
	return 0;
}

//High pass filter with cutoff frequency of approx. 0.03 * pi rad/sec (165 Hz for fs = 10 kHz)
float highPassFilter(float last_output, float input, float last_input){
	float output;
	output = 0.9 * last_output + input - last_input;
	return output;
	
}
