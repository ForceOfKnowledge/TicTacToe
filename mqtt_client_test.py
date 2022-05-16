import time
import mqtt_client
import threading


def on_message(client, userdata, message):
    print("---Message received---")
    print("Message: " + message.payload.decode("utf-8") + "\n")

if __name__ == '__main__':
    client = mqtt_client.MqttClient("banana", "localhost")

    fred1 = threading.Thread(target=client.listen, args=(on_message, ))
    fred1.start()
    time.sleep(1)

    client.send_message("Ich bin ein Berliner")
    print("Ende")
