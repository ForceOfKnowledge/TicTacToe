import socket  # for socket
import sys
import threading
from threading import Thread
import mqttsub
import argparse
import paho.mqtt.client as mqtt
import json
import time


class MyRobotConnection:

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

    def send(self, data):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Socket successfully created")
        except socket.error as err:
            print("socket creation failed with error %s", err)
        try:
            host_ip = socket.gethostbyname(self.hostname)
        except socket.gaierror:
            print("there was an error resolving the host")
            sys.exit()

        # connecting to the server
        s.connect((self.hostname, self.port))
        s.send(data)
        data = s.recv(1024)
        # print('Received', repr(data))
        time.sleep(0.2)
        s.close()
        return data


class RobotQueue:
    def __init__(self, hostname, port, filename):
        self._processing = False
        self.contentArray = []
        # cprogHostname="localhost"
        # cprogPort=3920
        self.filename = filename
        self.myRobotConnection = MyRobotConnection(hostname=hostname, port=port)

    def run(self, hostname, port):
        rc = 0
        self.hostname = hostname
        self.port = port
        while True:
            if self._processing == False:
                rc = self.loop()
            time.sleep(0.5)
        return rc

    def loop(self):
        if len(self.contentArray) == 0:
            return 0
        self._processing = True

        content = self.contentArray.pop(0)
        self.writeFile(self.filename, content)
        time.sleep(0.5)
        self.sendCRIcommand_Load()
        time.sleep(1)
        self.sendCRIcommand_Start()
        time.sleep(20)
        self._processing = False
        return 0

    def addRobotCommandToQueue(self, content):
        print("addRobotCommandToQueue")
        self.contentArray.append(content)

    def writeFile(self, filename, content):
        contentString = ''.join(content)
        print("writeFile filename: %s, len: %d" % (filename, len(contentString)))
        print(contentString)
        file = open(filename, "w")
        file.write(contentString)
        file.close()

    def sendCRIcommand_Load(self):
        self.sendCRICommand("CRISTART 1234 CMD LoadProgram tester.xml CRIEND")

    def sendCRIcommand_Start(self):
        self.sendCRICommand("CRISTART 1234 CMD StartProgram CRIEND")

    def sendCRICommand(self, command):
        print("sendCRIcommand: %s" % (command))
        dataReceived = self.myRobotConnection.send(bytearray(command.encode()))
        if dataReceived != None:
            print("Data received: ", dataReceived)
        print("Finished!")


class MyRobot:
    def __init__(self, filename, robot_host, robot_port):
        self.mqtt = mqttsub.MyMQTTClass(self.receiveMQTT)
        mqttThread = threading.Thread(target=self.mqtt.run, args=(hostname, mqtt_port, mqtt_topic))
        mqttThread.start()
        self.content = []
        self.robotQueue = RobotQueue(robot_host, robot_port, filename)
        queueThread = threading.Thread(target=self.robotQueue.run, args=(robot_host, robot_port))
        queueThread.start()

    def getPiecePosition(self, stationKey):
        robot_coords = {
            'x4': '<Linear AbortCondition="False" Nr="1" Source="Numerical" vel="45" acc="40" smooth="20" x="330" '
                  'y="150" z="100" a="-180" b="0" c="180" e1="0" e2="0" e3="0" Descr="" />',
            'x2': '<Linear AbortCondition="False" Nr="2" Source="Numerical" vel="45" acc="40" smooth="20" x="298" '
                  'y="135" z="100" a="-180" b="0" c="180" e1="0" e2="0" e3="0" Descr="" />',
            'x3': '<Linear AbortCondition="False" Nr="3" Source="Numerical" vel="45" acc="40" smooth="20" x="259" '
                  'y="156" z="100" a="-180" b="0" c="180" e1="0" e2="0" e3="0" Descr="" />',
            'x1': '<Linear AbortCondition="False" Nr="4" Source="Numerical" vel="45" acc="40" smooth="20" x="230" '
                  'y="153" z="100" a="-180" b="0" c="180" e1="0" e2="0" e3="0" Descr="" />',
            'x5': '<Linear AbortCondition="False" Nr="5" Source="Numerical" vel="45" acc="40" smooth="20" x="179" '
                  'y="160" z="100" a="-180" b="0" c="180" e1="0" e2="0" e3="0" Descr="" />',
            '11': '<Linear AbortCondition="False" Nr="1" Source="Numerical" vel="45" acc="40" smooth="0" x="338" '
                  'y="83" z="100" a="-180" b="0" c="180" e1="0" e2="0" e3="0" Descr="" />',
            '12': '<Linear AbortCondition="False" Nr="2" Source="Numerical" vel="45" acc="40" smooth="0" x="271" '
                  'y="78" z="100" a="-180" b="0" c="180" e1="0" e2="0" e3="0" Descr="" />',
            '13': '<Linear AbortCondition="False" Nr="3" Source="Numerical" vel="45" acc="40" smooth="0" x="182" '
                  'y="78" z="30" a="-180" b="0" c="180" e1="0" e2="0" e3="0" Descr="" />',
            '21': '<Linear AbortCondition="False" Nr="4" Source="Numerical" vel="45" acc="40" smooth="0" x="344" '
                  'y="0" z="100" a="-180" b="0" c="180" e1="0" e2="0" e3="0" Descr="" />',
            '22': '<Linear AbortCondition="False" Nr="5" Source="Numerical" vel="45" acc="40" smooth="0" x="265" '
                  'y="-5" z="100" a="-180" b="0" c="180" e1="0" e2="0" e3="0" Descr="" />',
            '23': '<Linear AbortCondition="False" Nr="6" Source="Numerical" vel="45" acc="40" smooth="0" x="184" '
                  'y="-7" z="100" a="-180" b="0" c="180" e1="0" e2="0" e3="0" Descr="" />',
            '31': '<Linear AbortCondition="False" Nr="7" Source="Numerical" vel="45" acc="40" smooth="0" x="346" '
                  'y="-75" z="100" a="-180" b="0" c="180" e1="0" e2="0" e3="0" Descr="" />',
            '32': '<Linear AbortCondition="False" Nr="8" Source="Numerical" vel="45" acc="40" smooth="0" x="269" '
                  'y="-82" z="100" a="-180" b="0" c="180" e1="0" e2="0" e3="0" Descr="" />',
            '33': '<Linear AbortCondition="False" Nr="9" Source="Numerical" vel="45" acc="40" smooth="0" x="187" '
                  'y="-85" z="100" a="-180" b="0" c="180" e1="0" e2="0" e3="0" Descr="" />',
            'o5': '<Linear AbortCondition="False" Nr="1" Source="Numerical" vel="45" acc="40" smooth="20" x="338" '
                  'y="-155" z="100" a="-180" b="19" c="180" e1="0" e2="0" e3="0" Descr="" />',
            'o2': '<Linear AbortCondition="False" Nr="2" Source="Numerical" vel="45" acc="40" smooth="20" x="309" '
                  'y="-140" z="100" a="-180" b="0" c="180" e1="0" e2="0" e3="0" Descr="" />',
            'o3': '<Linear AbortCondition="False" Nr="3" Source="Numerical" vel="45" acc="40" smooth="20" x="267" '
                  'y="-167" z="100" a="-180" b="0" c="180" e1="0" e2="0" e3="0" Descr="" />',
            'o4': '<Linear AbortCondition="False" Nr="4" Source="Numerical" vel="45" acc="40" smooth="20" x="237" '
                  'y="-149" z="100" a="-180" b="0" c="180" e1="0" e2="0" e3="0" Descr="" />',
            'o1': '<Linear AbortCondition="False" Nr="5" Source="Numerical" vel="45" acc="40" smooth="20" x="179" '
                  'y="-161" z="100" a="-180" b="0" c="180" e1="0" e2="0" e3="0" Descr="" />',
            }

        for coord in robot_coords:
            if coord == stationKey:
                return robot_coords[coord]
        assert 'getPiecePosition() Error'


    def createMoveCommand(self, coordfrom, coordto):
        print("create Move Command")
        content = ['<?xml version="1.0" encoding="utf-8"?>\n', '<Program>\n',
                   '<Header RobotName="Mover" RobotType="CPR_Mover4" GripperType="TwoFingerGripper.xml" '
                   'Software="CPRog V902-11-024" />\n',
                   '<Linear AbortCondition="False" Nr="1" Source="Numerical" vel="45" acc="40" smooth="0" x="240" '
                   'y="0" z="100" a="158.37" b="0" c="180" e1="0" e2="0" e3="0" Descr="" />\n',
                   '<Gripper Nr="1" Position="100" Descr="" />\n',
                   '%s\n' % coordfrom,
                   '<Relative AbortCondition="False" Nr="1" acc="100" smooth="0" MoType="cartbase" vel="45" x="0" '
                   'y="0" z="-55" e1="0" e2="0" e3="0" Descr="" />\n',
                   '<Gripper Nr="1" Position="0" Descr="" />\n',
                   '<Wait Nr="1" Type="Time" Seconds="0.5" Descr="" />\n',
                   '<Relative AbortCondition="False" Nr="1" acc="100" smooth="0" MoType="cartbase" vel="45" x="0" '
                   'y="0" z="55" e1="0" e2="0" e3="0" Descr="" />\n',
                   '%s\n' % coordto,
                   '<Relative AbortCondition="False" Nr="1" acc="100" smooth="0" MoType="cartbase" vel="45" x="0" '
                   'y="0" z="-55" e1="0" e2="0" e3="0" Descr="" />\n',
                   '<Gripper Nr="1" Position="100" Descr="" />\n',
                   '<Wait Nr="1" Type="Time" Seconds="0.75" Descr="" />\n',
                   '<Relative AbortCondition="False" Nr="1" acc="100" smooth="0" MoType="cartbase" vel="45" x="0" '
                   'y="0" z="55" e1="0" e2="0" e3="0" Descr="" />\n',
                   '<Linear AbortCondition="False" Nr="1" Source="Numerical" vel="45" acc="40" smooth="0" x="240" '
                   'y="0" z="100" a="158.37" b="0" c="180" e1="0" e2="0" e3="0" Descr="" />\n',
                   '</Program>\n']
        return content

    def receiveMQTT(self, mqttString):
        print("receiveMQTT(): Topic: ", mqttString.topic)
        payload = mqttString.payload.decode('utf-8')
        # print("Payload: ",payload)
        data = json.loads(payload)
        # msgType= data["type"]
        coordfrom = self.getPiecePosition(data['stationFrom'])
        coordto = self.getPiecePosition(data['stationTo'])
        # if not (msgType=="move"):
        #    print("MQTT received unknown message type: ", msgType)
        #    return
        print("createMoveCommand")
        content = self.createMoveCommand(coordfrom, coordto)
        # add Robot command to queue
        self.robotQueue.addRobotCommandToQueue(content)


hostname = "test.mosquitto.org"
mqtt_topic = "/game/tictactoe"
mqtt_port = 8080
filename = "C:/CPRog/Data/Programs/tester.xml"
robot_port = 3920
# MQTT topic for multi team mode
my_team = input("choose team nr: (1,2,...): ")
team_nr = 0
try:
    team_nr = int(my_team)
except:
    print("Error: This was not a number!")
    exit(1)
mqtt_topic = "/game/tictactoe/team"+str(team_nr)

robot_port = 3920
robot_host = "127.0.0.1"
robot = MyRobot(filename, robot_host, robot_port)
