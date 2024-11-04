import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QPushButton, QLabel, \
    QLineEdit
from PyQt5.QtCore import Qt
import requests


class LoginScreen(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.username = QLineEdit(self)
        self.username.setPlaceholderText("Username")
        self.password = QLineEdit(self)
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        login_button = QPushButton("Login", self)
        login_button.clicked.connect(self.login)

        layout.addWidget(QLabel("3CX Login", self))
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def login(self):
        username = self.username.text()
        password = self.password.text()
        success = self.app.client.login(username, password)
        if success:
            self.app.main_window.show_main_interface()
        else:
            print("Login failed")


class MainInterface(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.status_label = QLabel("Welcome to 3CX Client", self)
        self.call_button = QPushButton("Call User", self)
        self.call_button.clicked.connect(self.call_user)

        layout.addWidget(self.status_label)
        layout.addWidget(self.call_button)

        self.setLayout(layout)

    def call_user(self):
        # Call functionality here
        extension = "100"  # Example extension
        self.app.client.call_user(extension)


class ThreeCXClientApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = ThreeCXClient("https://147.185.221.23:5087/#/login")
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Enhanced 3CX Client")
        self.stacked_widget = QStackedWidget()

        self.login_screen = LoginScreen(self)
        self.main_interface = MainInterface(self)

        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.main_interface)

        self.setCentralWidget(self.stacked_widget)

    def show_main_interface(self):
        self.stacked_widget.setCurrentWidget(self.main_interface)

class ThreeCXClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None

    def login(self, username, password):
        login_url = f"{self.base_url}/login"

        # Step 1: Initialize session to get CSRF token or cookies if required
        initial_response = self.session.get(login_url)
        csrf_token = initial_response.cookies.get("csrf_token")  # Example; update based on 3CX specifics

        # Step 2: Attempt login with the token (if required by 3CX)
        headers = {
            "Content-Type": "application/json",
            "X-CSRF-Token": csrf_token if csrf_token else ""
        }
        payload = {"username": username, "password": password}
        response = self.session.post(login_url, json=payload, headers=headers)

        # Step 3: Check login success
        if response.status_code == 200 and "token" in response.json():
            self.token = response.json().get("token")
            self.session.headers.update({'Authorization': f"Bearer {self.token}"})
            print("Login successful!")
            return True
        else:
            print("Login failed:", response.status_code, response.text)
            return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = ThreeCXClientApp()
    main_window.show()
    sys.exit(app.exec_())
