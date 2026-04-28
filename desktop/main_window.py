from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
import requests
import pyperclip


class MainWindow(QWidget):
    def __init__(self, session_token, user_name):
        super().__init__()
        self.session_token = session_token
        self.user_name = user_name

        self.setWindowTitle("C-Lock Vault")
        self.resize(800, 450)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        title = QLabel(f"Welcome, {self.user_name}")
        self.layout.addWidget(title)

        self.load_vault_data()

    def load_vault_data(self):
        try:
            response = requests.post(
                "http://127.0.0.1:8765/vault/match",
                headers={
                    "Authorization": f"Bearer {self.session_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "domain": "clinix.cliniqon.com"
                }
            )

            data = response.json()

            matches = data.get("matches", [])
            if not matches:
                self.layout.addWidget(QLabel("No vault items available for this user/domain"))
                return

            for item in matches:
                self.add_vault_item(item)

        except Exception as e:
            self.layout.addWidget(QLabel(f"Error: {str(e)}"))

    def add_vault_item(self, item):
        row = QHBoxLayout()

        label = QLabel(f"{item['account_name']}  |  {item['login_username']}")

        copy_user_btn = QPushButton("Copy Username")
        copy_id_btn = QPushButton("Copy Vault ID")

        copy_user_btn.clicked.connect(
            lambda checked=False, value=item["login_username"]: self.copy_to_clipboard(value)
        )
        copy_id_btn.clicked.connect(
            lambda checked=False, value=str(item["vault_id"]): self.copy_to_clipboard(value)
        )

        row.addWidget(label)
        row.addWidget(copy_user_btn)
        row.addWidget(copy_id_btn)

        self.layout.addLayout(row)

    def copy_to_clipboard(self, text):
        pyperclip.copy(text)