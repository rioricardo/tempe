
#include <thread>
#include <vector>
#include <string>
#include <iostream>

void startConsumerThreads(const std::string& broker, const std::string& topic, int numThreads) {
    std::vector<std::thread> threads;
    
    // Create and start consumer threads
    for (int i = 0; i < numThreads; ++i) {
        threads.push_back(std::thread([broker, topic] {
            KafkaConsumer consumer(broker, topic);
            consumer.startConsuming();
        }));
    }

    // Join threads
    for (auto& t : threads) {
        t.join();
    }
}

int main() {
    std::string broker = "localhost:9092";  // Kafka broker address
    std::string topic = "your-topic";  // Kafka topic to consume messages from
    int numThreads = 4;  // Number of threads to handle messages concurrently

    // Start consumer threads
    startConsumerThreads(broker, topic, numThreads);

    return 0;
}
