#include "gpio_utils.c"

int main()
{
    unsigned int value[ADC_SAMPLE_NUM];
    int i;
    FILE * fd;
    
    fd = fopen("output.txt", "w+");
    
    ain_get_value(0, value);
    
    for (i=0; i < ADC_SAMPLE_NUM; i++){

    fprintf(fd, "%.4d \n", value[i]);
    }
    fclose(fd);
    return 0;
}