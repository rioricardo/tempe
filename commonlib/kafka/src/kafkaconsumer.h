#ifndef KAFKA_CONSUMER_H
#define KAFKA_CONSUMER_H

#include <librdkafka/rdkafkacpp.h>
#include <string>

class KafkaConsumer {
public:
    // Constructor: Initializes the Kafka consumer with broker and topic
    KafkaConsumer(const std::string& broker, const std::string& topicstr, const std::string& groupId, const std::string& offset);

    // Destructor: Cleans up Kafka consumer resources
    ~KafkaConsumer();

    // Starts consuming messages from the topic
    void startConsuming();

private:
    // Processes a single Kafka message
    void processMessage(RdKafka::Message* msg);

    RdKafka::KafkaConsumer* consumer;  // KafkaConsumer instance
    RdKafka::Conf* conf;               // Kafka configuration object
    std::string topicName;             // Topic name
};

#endif  // KAFKA_CONSUMER_H
