import os
from confluent_kafka import Producer, Consumer, KafkaException
from aws_msk_iam_sasl_signer import MSKTokenProvider

# Producer function
def produce_message(brokers, topic):
    # Create the SASL token for authentication using MSKTokenProvider
    token_provider = MSKTokenProvider(brokers)
    token = token_provider.get_token()

    producer_config = {
        'bootstrap.servers': brokers,
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'AWS_MSK_IAM',
        'sasl.username': 'unused',
        'sasl.password': token,  # Use the SASL token for authentication
    }

    producer = Producer(producer_config)
    try:
        producer.produce(topic, key="test-key", value="Hello, MSK!")
        producer.flush()
        print(f"Message sent to topic {topic}")
    except KafkaException as e:
        print(f"Error producing message: {e}")

# Consumer function
def consume_message(brokers, topic):
    # Create the SASL token for authentication using MSKTokenProvider
    token_provider = MSKTokenProvider(brokers)
    token = token_provider.get_token()

    consumer_config = {
        'bootstrap.servers': brokers,
        'group.id': 'test-group',
        'auto.offset.reset': 'earliest',
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'AWS_MSK_IAM',
        'sasl.username': 'unused',
        'sasl.password': token,  # Use the SASL token for authentication
    }

    consumer = Consumer(consumer_config)
    consumer.subscribe([topic])
    try:
        msg = consumer.poll(10.0)
        if msg:
            print(f"Received message: {msg.value().decode('utf-8')}")
        else:
            print("No message received within timeout.")
    finally:
        consumer.close()

# Lambda handler
def lambda_handler(event, context):
    brokers = os.environ['BROKERS']
    topic = os.environ['TOPIC']

    produce_message(brokers, topic)
    consume_message(brokers, topic)

    return {"statusCode": 200, "body": "Messages processed successfully"}
