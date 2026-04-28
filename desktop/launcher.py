import sys
import threading
import uvicorn
from PySide6.QtWidgets import QApplication
from desktop.login_window import LoginWindow
from app.config import settings


def start_api():
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False
    )


def start_desktop():
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()

    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())