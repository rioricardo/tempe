#include "kafkaconsumer.h"
#include <iostream>

KafkaConsumer::KafkaConsumer(const std::string& broker, const std::string& topicstr, const std::string& groupId, const std::string& offset)
    : topicName(topicstr) {
    // Create Kafka consumer configuration
    std::string errstr;
    conf = RdKafka::Conf::create(RdKafka::Conf::CONF_GLOBAL);

    // Set broker and group ID configuration
    if (conf->set("metadata.broker.list", broker, errstr) != RdKafka::Conf::CONF_OK) {
        throw std::runtime_error("Failed to set broker: " + errstr);
    }

    // Set the group ID for the consumer group
    if (conf->set("group.id", groupId, errstr) != RdKafka::Conf::CONF_OK) {
        throw std::runtime_error("Failed to set group.id: " + errstr);
    }

    // Set the offset
    if (conf->set("auto.offset.reset", offset, errstr) != RdKafka::Conf::CONF_OK) {
        throw std::runtime_error("Failed to set offset: " + errstr);
    }

    // Create the Kafka consumer
    consumer = RdKafka::KafkaConsumer::create(conf, errstr);
    if (!consumer) {
        throw std::runtime_error("Failed to create KafkaConsumer: " + errstr);
    }

    // Subscribe to the topic
    RdKafka::ErrorCode err = consumer->subscribe({topicName});
    if (err != RdKafka::ERR_NO_ERROR) {
        throw std::runtime_error("Failed to subscribe to topic: " + RdKafka::err2str(err));
    }
}


KafkaConsumer::~KafkaConsumer() {
    if (consumer) {
        consumer->close();
        delete consumer;
        consumer = nullptr;
    }
    if (conf) {
        delete conf;
        conf = nullptr;
    }
}

void KafkaConsumer::startConsuming() {
    while (true) {
        RdKafka::Message* msg = consumer->consume(1000);  // Consume with a 1-second timeout
        processMessage(msg);  // Process the consumed message
        delete msg;
    }
}

void KafkaConsumer::processMessage(RdKafka::Message* msg) {
    if (msg->err()) {
        if (msg->err() == RdKafka::ERR__TIMED_OUT) {
            // Ignore timeout errors
            return;
        }
        std::cerr << "Error: " << msg->errstr() << std::endl;
    } else {
        std::string data = std::string(static_cast<char*>(msg->payload()), msg->len());
        std::cout << "Received message: " << data << std::endl;
    }
}
