#include "kafkaproducer.h"

KafkaProducer::KafkaProducer(const std::string& broker, const std::string& topicstr)
    : topicName(topicstr), topic(nullptr), producer(nullptr), conf(nullptr) {
    std::string errstr;

    // Create Kafka configuration
    conf = RdKafka::Conf::create(RdKafka::Conf::CONF_GLOBAL);
    if (conf->set("metadata.broker.list", broker, errstr) != RdKafka::Conf::CONF_OK) {
        throw std::runtime_error("Failed to set broker: " + errstr);
    }

    // Create Kafka producer
    producer = RdKafka::Producer::create(conf, errstr);
    if (!producer) {
        throw std::runtime_error("Failed to create producer: " + errstr);
    }

    // Create topic object
    topic = RdKafka::Topic::create(producer, topicName, nullptr, errstr);
    if (!topic) {
        throw std::runtime_error("Failed to create topic: " + errstr);
    }
}

KafkaProducer::~KafkaProducer() {
    // Ensure all outstanding messages are sent before destroying producer
    if (producer) {
        producer->flush(10000);  // Wait up to 10 seconds
        delete topic;            // Clean up topic
        delete producer;         // Clean up producer
        delete conf;             // Clean up configuration
    }
}

void KafkaProducer::sendMessage(const std::string& message) {
    if (!producer || !topic) {
        throw std::runtime_error("Producer or topic is not initialized");
    }

    // Produce the message to the topic
    RdKafka::ErrorCode err = producer->produce(
        topic,                            // Topic object
        RdKafka::Topic::PARTITION_UA,     // Partition (use UA for automatic assignment)
        RdKafka::Producer::RK_MSG_COPY,  // Copy payload to Kafka internal buffer
        const_cast<char*>(message.c_str()),  // Pointer to the message payload
        message.size(),                   // Length of the payload
        nullptr,                          // Optional key pointer (pass nullptr for no key)
        nullptr                           // Optional opaque value
    );

    if (err != RdKafka::ERR_NO_ERROR) {
        std::cerr << "Failed to send message: " << RdKafka::err2str(err) << std::endl;
    } else {
        std::cout << "Message sent: " << message << std::endl;
    }

    // Poll for delivery reports to ensure the message is acknowledged
    producer->poll(0);
}
