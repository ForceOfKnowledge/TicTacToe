import paho.mqtt.client as client


class MqttClient(client.Client):

    def __init__(self, topic="test", host="test.mosquitto.org", port=1883):
        super().__init__()
        self.topic = topic
        self.port = port
        self.host = host

        self.connect(self.host, self.port)

    def listen(self, receive_method):
        self.on_message = receive_method
        self.subscribe(self.topic)
        self.loop_start()
        print("Started Listening to: " + self.topic + ", on Host: " + self.host + ", with Port: " + str(self.port))

        while input().casefold() != "exit".casefold() and input().casefold() != "quit".casefold():
            pass

        self.loop_stop()
        print("Stopped Listening")

    def on_message(self, client, userdata, message):
        print("---Message received---")
        print("Message: " + message.payload.decode("utf-8") + "\n")

    def send_message(self, message):
        self.publish(self.topic, message)
        print("---Message has been sent---")
        print("Message: " + message + "\n")
