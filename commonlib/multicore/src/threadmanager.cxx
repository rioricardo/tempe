#include "threadmanager.h"
#include "hardwareinfo.h"
#include <iostream>
#include <chrono>

// Constructor
ThreadManager::ThreadManager() : running(false) {}

// Destructor
ThreadManager::~ThreadManager() {
    stopThreads(); // Ensure threads are stopped on destruction
}

// Start threads
void ThreadManager::startThreads(std::function<void(int)> task) {
    
    unsigned int numCores = HardwareInfo::getHardwareCores();

    if (numCores == 0) {
        std::cerr << "Unable to detect the number of cores.\n";
        return;
    }

    std::cout << "Starting " << numCores << " threads.\n";
    running = true;

    for (unsigned int i = 0; i < numCores; ++i) {
        threads.emplace_back([this, task, i]() {
            while (running) {
                task(i); // Execute the task
                //std::this_thread::sleep_for(std::chrono::seconds(1)); // Simulate work
            }
        });
    }
}

// Stop threads
void ThreadManager::stopThreads() {
    if (!running) return; // Already stopped

    running = false;

    for (auto& thread : threads) {
        if (thread.joinable()) {
            thread.join();
        }
    }

    threads.clear();
    std::cout << "All threads stopped.\n";
}
