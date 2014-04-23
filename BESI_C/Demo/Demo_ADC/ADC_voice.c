#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>

#include "../../BBBio_lib/BBBiolib.h"
/* ------------------------------------------------------------ */
#define AUDIO_BUFFER_SIZE	4000
#define AUDIO_SAMPLE_RATE	4000
/* ----------------------------------------------------------- */
unsigned int buffer[AUDIO_BUFFER_SIZE*2] ={0};
int buf_size = 0;
FILE *adc_file;
/* ----------------------------------------------------------- */
#define NET_PORT	5005
#define NET_HOST	"YOUR IP"	/* your IP */
#define NET_BUFFER_SIZE 1028
/* ----------------------------------------------------------- */
void Tx_loop(void *argv)
{
    
   
    adc_file=fopen("adc_voice.txt", "w");
    int i;
    
	while(1) {
		if(buf_size > 0) {
		    for (i=0; i < buf_size; i++){
		        fprintf(adc_file, "%d\n", buffer[i]);
		    }
		    buf_size = 0;
		}
		usleep(10);
	}
}
/* ----------------------------------------------------------- */
int main(void)
{
	int i ,j;
	unsigned int *buf_ptr = &buffer[0];
	struct timeval t_start, t_end;
 	float mTime =0;
	int Tx_thread ;

	/* BBBIOlib init*/
	iolib_init();
	iolib_setdir(8,12, BBBIO_DIR_IN);

	/* using ADC_CALC toolkit to decide the ADC module argument .
	 *
	 *	#./ADC_CALC -f 44100 -t 30
	 *
	 *	Suggest Solution :
	 *		Clock Divider : 34 ,    Open Dly : 1 ,  Sample Average : 1 ,    Sample Dly : 1
	 */
	const int clk_div = 34 ;
	const int open_dly = 1;
	const int sample_dly = 1;

	BBBIO_ADCTSC_module_ctrl(BBBIO_ADC_WORK_MODE_TIMER_INT, clk_div);
	BBBIO_ADCTSC_channel_ctrl(BBBIO_ADC_AIN0, BBBIO_ADC_STEP_MODE_SW_CONTINUOUS, open_dly, \
				sample_dly, BBBIO_ADC_STEP_AVG_1, buffer, AUDIO_BUFFER_SIZE);

	pthread_create(&Tx_thread, NULL, &Tx_loop, NULL);

	for(i = 0 ; i < 2 ; i++) {
		/* fetch data from ADC */
		printf("sample\n");

		BBBIO_ADCTSC_channel_enable(BBBIO_ADC_AIN0);
		gettimeofday(&t_start, NULL);
		BBBIO_ADCTSC_work(AUDIO_BUFFER_SIZE);
		gettimeofday(&t_end, NULL);

		/* set transmit data size */
		buf_size = sizeof(int) * AUDIO_BUFFER_SIZE;

		mTime = (t_end.tv_sec -t_start.tv_sec)*1000000.0 +(t_end.tv_usec -t_start.tv_usec);
		mTime /=1000000.0f;
		
		printf("Sampling finish , First sample: %d fetch [%d] samples in %lfs\n", buffer[0], AUDIO_BUFFER_SIZE, mTime);
	}
	
	printf("finish\n");
	iolib_free();
	fclose(adc_file);
	return 0;
}



