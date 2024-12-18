#include "commonlib/kafka/src/kafkaconsumer.h"
#include <thread>
#include <vector>
#include <string>
#include <iostream>

void startConsumer(const std::string& broker, const std::string& topic, const std::string& groupid) {
    std::vector<std::thread> threads;
    
    KafkaConsumer consumer(broker, topic, groupid);
    consumer.startConsuming();

}

int main() {
    std::string broker = "goodboy:9092";  // Kafka broker address
    std::string topic = "test_topic";  // Kafka topic to consume messages from
    std::string groupid = "test_group";  // Kafka topic to consume messages from

    // Start consumer threads
    startConsumer(broker, topic, groupid);

    return 0;
}
