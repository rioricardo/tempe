#include "commonlib/kafka/src/kafkaconsumer.h"
#include <thread>
#include <vector>
#include <string>
#include <iostream>

void startConsumer(const std::string& broker, const std::string& topic, const std::string& groupid,  const std::string& offset) {
    std::vector<std::thread> threads;
    
    KafkaConsumer consumer(broker, topic, groupid, offset);
    consumer.startConsuming();

}

int main() {
    std::string broker = "goodboy:9092,smugboy:9092";  // Kafka broker address
    std::string topic = "test_topic";  // Kafka topic to consume messages from
    std::string groupid = "test_group1";  // Kafka topic to consume messages from
    std::string offset = "latest";  // Kafka topic to consume messages from

    // Start consumer threads
    startConsumer(broker, topic, groupid, offset);

    return 0;
}
