from interface import KafkaConsumerUOW

for event_message in KafkaConsumerUOW().gen_pool_messages_from_topics():
    q = 1
