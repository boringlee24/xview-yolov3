import zmq

context = zmq.Context()

# Producer
producer = context.socket(zmq.PUSH)
producer.bind("tcp://127.0.0.1:5555")

# Consumer
consumer = context.socket(zmq.PULL)
consumer.connect("tcp://127.0.0.1:5555")

# Sending data
data = "Hello from producer"
producer.send_string(data)

# Receiving data
received_data = consumer.recv_string()
print(f"Received: {received_data}")

# Clean up
producer.close()
consumer.close()
context.term()
