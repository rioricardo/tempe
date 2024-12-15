#include <librdkafka/rdkafkacpp.h>
#include <iostream>
#include <thread>
#include <vector>
#include <string>

class KafkaConsumer {
public:
    KafkaConsumer(const std::string& broker, const std::string& topic) : topicName(topic) {
        // Create Kafka consumer configuration
        std::string errstr;
        conf = RdKafka::Conf::create(RdKafka::Conf::CONF_GLOBAL);
        
        conf->set("metadata.broker.list", broker, errstr);
        
        // Create the consumer
        consumer = RdKafka::Consumer::create(conf, errstr);
        
        // Subscribe to the topic
        RdKafka::ErrorCode err = consumer->subscribe({topic});
        if (err != RdKafka::ERR_NO_ERROR) {
            std::cerr << "Error subscribing to topic: " << RdKafka::err2str(err) << std::endl;
        }
    }

    void startConsuming() {
        while (true) {
            RdKafka::Message* msg = consumer->consume(1000);  // Consume message with timeout (1 sec)
            processMessage(msg);  // Process the consumed message
            delete msg;
        }
    }

private:
    void processMessage(RdKafka::Message* msg) {
        if (msg->err()) {
            std::cerr << "Error: " << msg->errstr() << std::endl;
        } else {
            std::string data = std::string(static_cast<char*>(msg->payload()), msg->len());
            std::cout << "Received message: " << data << std::endl;
            // Process the message (e.g., insert into Aerospike or any other processing)
        }
    }

    RdKafka::Consumer* consumer;
    RdKafka::Conf* conf;
    std::string topicName;
};

