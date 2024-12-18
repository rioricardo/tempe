#include "commonlib/kafka/src/kafkaproducer.h"
#include "commonlib/multicore/src/hardwareinfo.h"
#include "commonlib/multicore/src/threadmanager.h"
#include <iostream>
#include <string>

// Task for each thread
void produceMessagesTask(KafkaProducer& producer, int threadId) {
    std::string message = "Thread " + std::to_string(threadId) + " - Message at " + std::to_string(std::time(nullptr));
    producer.sendMessage(message);
}

int main() {
    try {
        // Initialize the Kafka producer
        KafkaProducer producer("goodboy:9092", "test_topic");

        // Initialize the thread manager
        ThreadManager threadManager;

        // Start threads with the producer task
        threadManager.startThreads([&producer](int threadId) {
            produceMessagesTask(producer, threadId);
        });

        std::cout << "Press Enter to stop the threads...\n";
        std::cin.get(); // Wait for user input to stop threads

        // Stop threads
        threadManager.stopThreads();

    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << std::endl;
        return 1;
    }

    return 0;
}
