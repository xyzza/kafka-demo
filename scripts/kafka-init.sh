#!/usr/bin/env sh
set -e

BOOTSTRAP_SERVER="${KAFKA_BOOTSTRAP_SERVER:-broker-1:19092}"
TOPIC="${KAFKA_TOPIC:-demo_topic}"
PARTITIONS="${KAFKA_TOPIC_PARTITIONS:-4}"

echo "Waiting for Kafka broker at ${BOOTSTRAP_SERVER}..."
until /opt/kafka/bin/kafka-topics.sh --bootstrap-server "$BOOTSTRAP_SERVER" --list > /dev/null 2>&1; do
    sleep 1
done

echo "Creating topic '${TOPIC}' with ${PARTITIONS} partitions..."
/opt/kafka/bin/kafka-topics.sh \
    --bootstrap-server "$BOOTSTRAP_SERVER" \
    --create \
    --topic "$TOPIC" \
    --partitions "$PARTITIONS" \
    --if-not-exists

echo "Topic '${TOPIC}' is ready."
/opt/kafka/bin/kafka-topics.sh \
    --bootstrap-server "$BOOTSTRAP_SERVER" \
    --describe \
    --topic "$TOPIC"
