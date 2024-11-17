#include <iostream>
#include "commonlib/multicore/src/hardwareinfo.h"

int main() {
    unsigned int cores = HardwareInfo::getHardwareCores();
    
    std::cout << "Hardware Cores: " << cores << std::endl;
   
    return 0;
}
