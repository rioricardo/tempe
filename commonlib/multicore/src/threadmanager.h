#ifndef THREAD_MANAGER_H
#define THREAD_MANAGER_H

#include <thread>
#include <vector>
#include <atomic>
#include <functional>

class ThreadManager {
public:
    ThreadManager();
    ~ThreadManager();

    void startThreads(std::function<void(int)> task);
    void stopThreads();

private:
    std::vector<std::thread> threads;
    std::atomic<bool> running;
};

#endif // THREAD_MANAGER_H
