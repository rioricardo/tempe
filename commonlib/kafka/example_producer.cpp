#include <thread>
#include <vector>
#include <string>
#include <iostream>

int main() {
    std::string broker = "localhost:9092";  // Kafka broker address
    std::string topic = "your-topic";      // Kafka topic name

    try {
        // Create producer
        KafkaProducer producer(broker, topic);

        // Send some test messages
        for (int i = 0; i < 10; ++i) {
            std::string message = "Hello Kafka! Message #" + std::to_string(i);
            producer.sendMessage(message);
        }
    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << std::endl;
        return 1;
    }

    return 0;
}
