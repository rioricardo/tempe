#ifndef HARDWAREINFO_H
#define HARDWAREINFO_H

class HardwareInfo {
public:
    // Returns the number of hardware cores available on the system
    static unsigned int getHardwareCores();
};

#endif // HARDWAREINFO_H

