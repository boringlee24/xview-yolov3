import zmq

context = zmq.Context()

# Producer
producer = context.socket(zmq.PUSH)
producer.bind("tcp://127.0.0.1:5555")

# Sending data
data = "100"
producer.send_string(data)

producer.close()
context.term()
