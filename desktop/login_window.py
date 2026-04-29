from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
import requests
from desktop.main_window import MainWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("C-Lock Login")
        self.resize(320, 180)

        self.label = QLabel("Login to C-Lock")

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.button = QPushButton("Login")
        self.button.clicked.connect(self.handle_login)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.email)
        layout.addWidget(self.password)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def handle_login(self):
        try:
            response = requests.post(
                "https://c-lock-1.onrender.com/auth/login",
                json={
                    "email": self.email.text(),
                    "password": self.password.text()
                }
            )

            data = response.json()

            if data.get("success"):
                QMessageBox.information(self, "Success", data["message"])
                self.main_window = MainWindow(
                    session_token=data["access_token"],
                    refresh_token=data["refresh_token"],
                    user_name=data["name"]
                )
                self.main_window.show()
                self.close()
            else:
                QMessageBox.warning(self, "Error", data.get("message", "Login failed"))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))