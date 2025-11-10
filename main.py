import sys
from PyQt6.QtWidgets import QApplication
from code.auth_window import AuthWindow
from code.main_window import MainWindow


class AppController:
    def __init__(self):
        print("test")

        self.auth_window = AuthWindow()
        self.main_window = None

        # сигнал успешного входа
        self.auth_window.login_success.connect(self.open_main_window)

        self.auth_window.show()

    def open_main_window(self, user_id, username):
        print(f"главное окно для пользователя")
        self.main_window = MainWindow(user_id, username)
        self.auth_window.close()
        self.main_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = AppController()
    sys.exit(app.exec())
