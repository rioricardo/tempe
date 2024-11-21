#include <iostream>
#include <thread>
#include <vector>
#include <atomic>
#include <chrono>
#include "commonlib/multicore/src/hardwareinfo.h"
#include "commonlib/multicore/src/threadmanager.h"


void threadTask(int threadId) {
    std::cout << "Thread " << threadId << " is running\n";
    // Simulate some work
    // std::this_thread::sleep_for(std::chrono::seconds(1));
}


int main() {
    ThreadManager threadManager;

    // Start threads
    threadManager.startThreads(threadTask);

    // Simulate running for a while
    std::this_thread::sleep_for(std::chrono::seconds(5));

    // Stop threads
    threadManager.stopThreads();

    return 0;
}

