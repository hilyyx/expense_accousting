from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Учёт личных расходов")
        self.setGeometry(300, 200, 800, 600)
        self.setStyleSheet("background-color: #D3D3D3; color: black;")

        label = QLabel("Добро пожаловать в приложение 'Учёт личных расходов'!", self)
        label.move(180, 250)
        label.resize(450, 30)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
