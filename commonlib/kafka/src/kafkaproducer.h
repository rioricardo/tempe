#ifndef KAFKAPRODUCER_H
#define KAFKAPRODUCER_H

#include <librdkafka/rdkafkacpp.h>
#include <string>
#include <stdexcept>
#include <iostream>

// KafkaProducer class to handle Kafka message production
class KafkaProducer {
public:
    /**
     * Constructor to initialize the Kafka producer.
     * @param broker The broker list as a comma-separated string (e.g., "localhost:9092").
     * @param topic The name of the topic to produce messages to.
     */
    KafkaProducer(const std::string& broker, const std::string& topicstr);

    /**
     * Destructor to clean up resources.
     */
    ~KafkaProducer();

    /**
     * Sends a message to the Kafka topic.
     * @param message The message to be sent.
     */
    void sendMessage(const std::string& message);

private:
    std::string topicName;               // Topic name
    RdKafka::Topic* topic;               // Kafka Topic object
    RdKafka::Producer* producer;         // Kafka Producer object
    RdKafka::Conf* conf;                 // Kafka configuration
};

#endif // KAFKAPRODUCER_H
