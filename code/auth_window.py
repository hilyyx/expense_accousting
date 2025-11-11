from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from code.database import Database


class AuthWindow(QWidget):
    login_success = pyqtSignal(int, str) # открытие главного экрана id, username

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация — Учёт личных расходов")
        self.setGeometry(500, 300, 400, 250)
        self.setStyleSheet("background-color: #D3D3D3; color: black;")

        self.db = Database()
        self.init_ui()

    def init_ui(self):
        title = QLabel("Добро пожаловать!")
        title.setFont(QFont("Arial", 16))
        title.setStyleSheet("color: black;")

        self.username = QLineEdit()
        self.username.setPlaceholderText("Имя пользователя")
        self.username.setStyleSheet("background-color: white; color: black;")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Пароль")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setStyleSheet("background-color: white; color: black;")

        login_button = QPushButton("Войти")
        login_button.setStyleSheet("background-color: white; color: black;")
        register_button = QPushButton("Регистрация")
        register_button.setStyleSheet("background-color: white; color: black;")

        login_button.clicked.connect(self.login)
        register_button.clicked.connect(self.register)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.username)
        layout.addWidget(self.password)

        buttons = QHBoxLayout()
        buttons.addWidget(login_button)
        buttons.addWidget(register_button)
        layout.addLayout(buttons)

        self.setLayout(layout)

    def login(self):
        username = self.username.text()
        password = self.password.text()

        if not username or not password:
            self.show_message("Ошибка", "Заполните все поля!")
            return

        success, user_id = self.db.login_user(username, password)
        
        if success:
            print(f"Успешный вход {username} с id: {user_id}")
            self.login_success.emit(user_id, username)
        else:
            self.show_message("Ошибка", "Неверное имя пользователя или пароль")

    def register(self):
        username = self.username.text()
        password = self.password.text()

        if not username or not password:
            self.show_message("Ошибка", "Заполните все поля")
            return

        success, result = self.db.register_user(username, password)
        
        if success:
            login_success, user_id = self.db.login_user(username, password)
            if login_success:
                self.db.get_default_categories(user_id)
            self.show_message("Успех", "Регистрация прошла успешно! Теперь можно войти")
            self.password.clear()
        else:
            self.show_message("Ошибка", result)

    def show_message(self, title, text):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.exec()
