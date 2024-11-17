#include "hardwareinfo.h"
#include <thread>

// Implementation of getHardwareCores() function
unsigned int HardwareInfo::getHardwareCores() {
    return std::thread::hardware_concurrency();
}

