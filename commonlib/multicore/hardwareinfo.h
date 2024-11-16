#ifndef HARDWAREINFO_H
#define HARDWAREINFO_H

#ifdef _WIN32
    #define EXPORT __declspec(dllexport)
#else
    #define EXPORT
#endif

class HardwareInfo {
public:
    // Returns the number of hardware cores available on the system
    static EXPORT unsigned int getHardwareCores();
};


#endif // HARDWAREINFO_H

