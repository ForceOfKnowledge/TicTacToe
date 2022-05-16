import random
import sys
import time
import mqtt_client
import threading

from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QIcon, QFont, QPixmap, QWindow
from PyQt5.QtWidgets import QApplication, QPushButton, QToolTip, QLabel, QMainWindow, QAction, QWidget, QTextEdit, \
    QLineEdit


class Board(QMainWindow):
    gameState = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    prefix = QFont("Z003", 16)

    window_pos_x = 60
    window_pos_y = 60
    window_width = 420
    window_height = 500

    button_width = 100
    button_height = 100
    default_button_pos_x = 30
    default_button_pos_y = 100
    space_between_lines = 100
    space_between_buttons = 70

    reset_button_pos_x = 170
    reset_button_pos_y = 20

    winner_text_pos_x = 90
    winner_text_pos_y = 340

    active_player_text_pos_x = 110
    active_player_text_pos_y = 320

    error_text_pos_x = 90
    error_text_pos_y = 350

    def __init__(self):
        super().__init__()
        self.hide()
        self.init_buttons()
        self.init_window()
        self.init_menu()
        self.init_labels()

    def init_buttons(self):
        QToolTip.setFont(self.prefix)

        self.buttons = []
        for i in range(0, 9):
            self.buttons.append(QPushButton("", self))
            self.buttons[len(self.buttons) - 1].setStyleSheet(
                "border-style: solid; border-width: 3px; border-color: black; background-color: white;")
            self.buttons[len(self.buttons) - 1].setIconSize(
                QtCore.QSize(self.button_width - 15, self.button_height - 10))

            if range(0, 3).__contains__(i):
                self.buttons[len(self.buttons) - 1].setGeometry(
                    self.default_button_pos_x * (i + 1) + self.space_between_buttons * i,
                    self.default_button_pos_y + self.space_between_lines * 0, self.button_width, self.button_height)
                continue

            if range(3, 6).__contains__(i):
                self.buttons[len(self.buttons) - 1].setGeometry(
                    self.default_button_pos_x * (i - 2) + self.space_between_buttons * (i - 3),
                    self.default_button_pos_y + self.space_between_lines * 1, self.button_width, self.button_height)
                continue

            if range(6, 9).__contains__(i):
                self.buttons[len(self.buttons) - 1].setGeometry(
                    self.default_button_pos_x * (i - 5) + self.space_between_buttons * (i - 6),
                    self.default_button_pos_y + self.space_between_lines * 2, self.button_width, self.button_height)
                continue

        self.reset_button = QPushButton("Reset", self)
        self.reset_button.setGeometry(self.reset_button_pos_x, self.reset_button_pos_y, 80, 30)
        self.reset_button.setEnabled(False)
        self.reset_button.setToolTip("Reset Game")
        self.reset_button.clicked.connect(self.reset)
        self.reset_button.setIcon(QIcon("rsc/reset_button.jpeg"))

    def init_labels(self):
        QToolTip.setFont(self.prefix)

        self.winner_text = QLabel("", self)
        self.winner_text.setGeometry(self.winner_text_pos_x, self.default_button_pos_y + self.winner_text_pos_y, 200, 30)
        self.winner_text.setFont(self.prefix)
        self.winner_text.hide()

        self.active_player_text = QLabel("Active Player", self)
        self.active_player_text.setGeometry(self.active_player_text_pos_x, self.default_button_pos_y + self.active_player_text_pos_y, 200, 30)
        self.active_player_text.setFont(self.prefix)
        self.active_player_text.setToolTip("Current player")
        self.active_player_text.show()

        self.error_text = QLabel("ERROR", self)
        self.error_text.setGeometry(self.error_text_pos_x, self.default_button_pos_y + self.error_text_pos_y, 300, 30)
        self.error_text.setStyleSheet("color: rgb(255, 0, 0)")
        self.error_text.setFont(self.prefix)
        self.error_text.hide()

    def init_window(self):
        self.setWindowTitle("My GUI")
        self.setGeometry(self.window_pos_x, self.window_pos_x, self.window_width, self.window_height)
        self.setStyleSheet("background-color: white;")

    def init_menu(self):
        reset = QAction(QIcon("rsc/reset_button.jpeg"), "&Force Reset", self)
        reset.setShortcut("Ctrl+R")
        reset.setStatusTip("Force Reset")
        reset.triggered.connect(self.reset)

        menubar = self.menuBar()
        game = menubar.addMenu("&Game")
        game.addAction(reset)

    def reset(self):
        for i in range(0, len(self.gameState)):
            self.gameState[i] = 0
        self.reset_button.setEnabled(False)
        self.winner_text.hide()
        for button in self.buttons:
            button.setIcon(QIcon(QPixmap(1, 1)))
            button.setText("")
        self.active_player_text.show()


class PlayerFinderScreen(QWindow):
    def __init__(self):
        super().__init__()

        self.widget = QWidget(self)
        self.init_window()
        self.init_labels()
        self.init_buttons()

        self.show()

    def init_labels(self):
        self.password_text = QLineEdit(self.widget)
        self.password_text.setText("Put the Game Code here.")
        self.password_text.show()

        self.status_text = QLabel("", self.widget)
        self.status_text.show()

    def init_buttons(self):
        self.submit_button = QPushButton("Submit", self.widget)

    def init_window(self):
        self.setGeometry(100, 100, 50, 50)


class Player:
    def __init__(self, id, icon):
        self.id = id
        self.icon = icon


class Game:
    draw = False
    win_states = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 4, 8], [2, 4, 6], [0, 3, 6], [1, 4, 7], [2, 5, 8]]

    def __init__(self):
        self.board = Board()

        self.pfs = PlayerFinderScreen()

        self.client = mqtt_client.MqttClient()
        self.fred1 = threading.Thread(target=self.client.listen, args=(self.on_message_received,))
        self.fred1.start()
        print("Waiting a Second...")
        time.sleep(1)

    def start(self):
        self.symbol1 = QIcon(QPixmap("rsc/symbol1.png"))
        self.symbol2 = QIcon(QPixmap("rsc/symbol2.png"))

        for button in self.board.buttons:
            button.clicked.connect(self.on_click)

        self.players = [Player(1, self.symbol1), Player(2, self.symbol2)]

        self.active_player = self.players[random.randint(0, 1)]
        self.board.active_player_text.setText("Spieler " + str(self.active_player.id) + " ist am Zug.")

        self.board.show()

    def game_active(self):
        for win_state in self.win_states:
            cache = self.board.gameState[win_state[0]]
            if cache == 0:
                continue
            for i in win_state:
                if cache != self.board.gameState[i]:
                    break

            else:
                draw = True
                for j in self.board.gameState:
                    if j != cache:
                        draw = False

                self.draw = draw
                return False

        return True

    def on_click(self):
        QToolTip.setFont(self.board.prefix)
        button = self.board.sender()
        self.board.error_text.hide()
        if button.text() == "":
            if self.game_active():
                button.setIcon(self.active_player.icon)

                s = ""
                for i in range(0, self.active_player.id):
                    s += " "
                button.setText(s)

                for i in range(0, len(self.board.buttons)):
                    if self.board.buttons[i].text() == " ":
                        self.board.gameState[i] = 1
                    elif self.board.buttons[i].text() == "  ":
                        self.board.gameState[i] = 2
                    else:
                        pass

                if not self.game_active():
                    if self.draw:
                        self.board.winner_text.setText("Unentschieden!")
                    else:
                        self.board.winner_text.setText("Spieler " + str(self.active_player.id) + " hat gewonnen.")
                        self.board.active_player_text.hide()
                    self.board.winner_text.show()
                    self.board.reset_button.setEnabled(True)
                    self.draw = 0
                    self.active_player = self.players[random.randint(0, 1)]
                    return

        else:
            if self.game_active():
                self.board.error_text.setText("Dieses Feld ist schon vergeben!")
                self.board.error_text.show()
            return

        if self.active_player == self.players[0]:
            self.active_player = self.players[1]
        else:
            self.active_player = self.players[0]
        self.board.active_player_text.setText("Spieler " + str(self.active_player.id) + " ist am Zug.")

    def on_message_received(self, client, userdata, message):
        print("---Message received---")
        print("Message: " + message.payload.decode("utf-8") + "\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = Game()

    sys.exit(app.exec_())
