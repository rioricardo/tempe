#include <librdkafka/rdkafkacpp.h>
#include <iostream>
#include <thread>
#include <vector>
#include <string>

class KafkaProducer {
public:
    KafkaProducer(const std::string& broker, const std::string& topic)
        : topicName(topic) {
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
    }

    ~KafkaProducer() {
        // Ensure all outstanding messages are sent before destroying producer
        producer->flush(10000);  // Wait up to 10 seconds
        delete producer;
        delete conf;
    }

    void sendMessage(const std::string& message) {
        // Produce the message to the topic
        RdKafka::ErrorCode err = producer->produce(
            topicName,  // Topic name
            RdKafka::Topic::PARTITION_UA,  // Partition (use UA for automatic assignment)
            RdKafka::Producer::RK_MSG_COPY,  // Copy payload to Kafka internal buffer
            const_cast<char*>(message.c_str()),  // Payload (message content)
            message.size(),  // Payload size
            nullptr,  // Optional key
            nullptr   // Optional opaque value
        );

        if (err != RdKafka::ERR_NO_ERROR) {
            std::cerr << "Failed to send message: " << RdKafka::err2str(err) << std::endl;
        } else {
            std::cout << "Message sent: " << message << std::endl;
        }

        // Poll for delivery reports to ensure the message is acknowledged
        producer->poll(0);
    }

private:
    RdKafka::Producer* producer = nullptr;
    RdKafka::Conf* conf = nullptr;
    std::string topicName;
};
