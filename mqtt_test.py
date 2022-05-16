import paho.mqtt.client as mqtt


def on_message(client, userdata, message):
    print("---Message received---")
    print("Message: " + message.payload.decode("utf-8") + "\n")

if __name__ == "__main__":
    topic = "banana"
    host = "test.mosquitto.org"
    port = 1883
    
    client = mqtt.Client("Micky")
    #client.publish(topic, "keks")
    client.connect(host, port)
    client.on_message = on_message
    client.subscribe(topic)
    client.loop_start()
    print("Started Listening to: " + topic + ", on Host: " + host + ", with Port: " + str(port))

    while input().casefold() != "exit".casefold() and input().casefold() != "quit".casefold():
        pass

    client.loop_stop()
    print("Stopped Listening")
