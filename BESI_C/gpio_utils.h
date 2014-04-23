#define SYSFS_GPIO_DIR "/sys/class/gpio"
#define MAX_BUF 64

int gpio_export(unsigned int gpio);
int gpio_unexport(unsigned int gpio);
int gpio_set_dir(unsigned int gpio, const char* dir);
int gpio_set_value(unsigned int gpio, unsigned int value);
int gpio_get_value(unsigned int gpio, unsigned int *value);
int gpio_set_edge(unsigned int gpio, const char *edge);
int gpio_fd_open(unsigned int gpio, unsigned int dir);
int gpio_fd_close(int fd);

// Analog in
#define ADC_BUF 1024
#define ADC_SAMPLE_NUM 1000
#define SYSFS_AIN_DIR "/sys/devices/ocp.3/helper.15"
int ain_get_value(unsigned int ain, unsigned int *value);