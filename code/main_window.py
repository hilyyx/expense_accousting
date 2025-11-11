from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLineEdit, QComboBox, QDateEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QCheckBox,
    QMessageBox, QVBoxLayout, QHBoxLayout, QGridLayout, QHeaderView
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QPixmap
from code.database import Database
from code.statistics_window import StatisticsWindow
import os


class MainWindow(QMainWindow):
    def __init__(self, user_id, username):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.db = Database()
        self.editing_transaction_id = None

        self.setWindowTitle(f"Учёт личных расходов — {username}")
        self.setGeometry(200, 100, 1200, 800)
        self.setStyleSheet("background-color: #D3D3D3; color: black;")

        if not self.db.get_categories(self.user_id):
            self.db.get_default_categories(self.user_id)

        self.init_ui()
        self.load_transactions()
        self.update_balance()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        widget_style = "background-color: white; color: black;"
        button_style = "background-color: white; color: black; padding: 5px;"

        title_layout = QHBoxLayout()
        title_label = QLabel(f"Учёт расходов — {self.username}")
        title_label.setFont(QFont("Arial", 14))
        title_label.setStyleSheet("color: black; padding: 5px;")
        title_layout.addWidget(title_label)

        image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "res", "money_icon.png")
        icon_label = QLabel()
        pixmap = QPixmap(image_path)
        icon_label.setPixmap(pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        title_layout.addWidget(icon_label)
        
        title_layout.addStretch()
        title_widget = QWidget()
        title_widget.setLayout(title_layout)
        main_layout.addWidget(title_widget)
        
        form_group = QWidget()
        form_group.setStyleSheet("background-color: white; padding: 10px;")
        form_layout = QGridLayout()
        form_group.setLayout(form_layout)
        
        form_layout.addWidget(QLabel("Тип:"), 0, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["доход", "расход"])
        self.type_combo.setStyleSheet(widget_style)
        self.type_combo.currentTextChanged.connect(self.update_categories)
        form_layout.addWidget(self.type_combo, 0, 1)
        
        form_layout.addWidget(QLabel("Категория:"), 0, 2)
        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet(widget_style)
        self.update_categories()
        form_layout.addWidget(self.category_combo, 0, 3)
        
        form_layout.addWidget(QLabel("Сумма:"), 1, 0)
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        self.amount_input.setStyleSheet(widget_style)
        form_layout.addWidget(self.amount_input, 1, 1)
        
        form_layout.addWidget(QLabel("Дата:"), 1, 2)
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setStyleSheet(widget_style)
        form_layout.addWidget(self.date_input, 1, 3)
        
        form_layout.addWidget(QLabel("Описание:"), 2, 0)
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Описание...")
        self.description_input.setStyleSheet(widget_style)
        form_layout.addWidget(self.description_input, 2, 1, 1, 3)
        
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить")
        self.add_button.setStyleSheet(button_style)
        self.add_button.clicked.connect(self.add_transaction)
        
        self.edit_button = QPushButton("Сохранить изменения")
        self.edit_button.setStyleSheet(button_style)
        self.edit_button.clicked.connect(self.save_transaction)
        self.edit_button.setEnabled(False)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setStyleSheet(button_style)
        self.cancel_button.clicked.connect(self.cancel_edit)
        self.cancel_button.setEnabled(False)
        
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.cancel_button)
        form_layout.addLayout(buttons_layout, 3, 0, 1, 4)
        main_layout.addWidget(form_group)

        filters_group = QWidget()
        filters_group.setStyleSheet("background-color: white; padding: 10px;")
        filters_layout = QHBoxLayout()
        filters_group.setLayout(filters_layout)
        
        filters_layout.addWidget(QLabel("Поиск:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по описанию...")
        self.search_input.setStyleSheet(widget_style)
        self.search_input.textChanged.connect(self.load_transactions)
        filters_layout.addWidget(self.search_input)
        
        self.expenses_only_checkbox = QCheckBox("Показать только расходы")
        self.expenses_only_checkbox.setStyleSheet("color: black;")
        self.expenses_only_checkbox.stateChanged.connect(self.load_transactions)
        filters_layout.addWidget(self.expenses_only_checkbox)
        main_layout.addWidget(filters_group)
        
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels(["ID", "Тип", "Категория", "Сумма", "Дата", "Описание"])
        self.transactions_table.setStyleSheet(widget_style)
        self.transactions_table.horizontalHeader().setStyleSheet("background-color: #E0E0E0; color: black;")
        self.transactions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.transactions_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.transactions_table.setSortingEnabled(True)
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.transactions_table)
        
        buttons_group = QWidget()
        buttons_group.setStyleSheet("background-color: white; padding: 10px;")
        buttons_layout = QHBoxLayout()
        buttons_group.setLayout(buttons_layout)
        
        edit_button = QPushButton("Редактировать выбранную запись")
        edit_button.setStyleSheet(button_style)
        edit_button.clicked.connect(self.edit_selected_transaction)
        buttons_layout.addWidget(edit_button)
        
        delete_button = QPushButton("Удалить выбранную запись")
        delete_button.setStyleSheet(button_style)
        delete_button.clicked.connect(self.delete_transaction)
        buttons_layout.addWidget(delete_button)
        
        buttons_layout.addStretch()
        
        statistics_button = QPushButton("Статистика")
        statistics_button.setStyleSheet(button_style)
        statistics_button.clicked.connect(self.open_statistics)
        buttons_layout.addWidget(statistics_button)
        main_layout.addWidget(buttons_group)
        
        info_group = QWidget()
        info_group.setStyleSheet("background-color: white; padding: 15px;")
        info_layout = QHBoxLayout()
        info_group.setLayout(info_layout)
        
        self.balance_label = QLabel("Баланс: 0.00 ₽")
        self.balance_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.balance_label.setStyleSheet("color: black;")
        info_layout.addWidget(self.balance_label)
        
        info_layout.addStretch()
        
        self.income_label = QLabel("Доходы: 0.00 ₽")
        self.income_label.setStyleSheet("color: green;")
        info_layout.addWidget(self.income_label)
        
        self.expense_label = QLabel("Расходы: 0.00 ₽")
        self.expense_label.setStyleSheet("color: red;")
        info_layout.addWidget(self.expense_label)
        main_layout.addWidget(info_group)

    def update_categories(self):
        current_type = self.type_combo.currentText() if hasattr(self, 'type_combo') else "доход"
        category_type = 0 if current_type == "доход" else 1
        categories = self.db.get_categories(self.user_id, category_type)
        self.category_combo.clear()
        self.category_dict = {cat_name: cat_id for cat_id, cat_name, _ in categories}
        self.category_combo.addItems([cat_name for _, cat_name, _ in categories])

    def _get_transaction_data(self):
        try:
            amount = float(self.amount_input.text().replace(",", "."))
            if amount <= 0:
                raise ValueError
        except ValueError:
            self.show_message("Ошибка", "Введите корректную сумму!")
            return None
        
        transaction_type = self.type_combo.currentText()
        category_name = self.category_combo.currentText()
        
        if not hasattr(self, 'category_dict') or category_name not in self.category_dict:
            self.show_message("Ошибка", "Выберите категорию!")
            return None
        
        return {
            'type': transaction_type,
            'category_id': self.category_dict[category_name],
            'amount': amount,
            'date': self.date_input.date().toString("yyyy-MM-dd"),
            'description': self.description_input.text().strip() or "Без описания"
        }

    def add_transaction(self):
        data = self._get_transaction_data()
        if not data:
            return
        
        self.db.add_transaction(self.user_id, data['type'], data['category_id'], 
                               data['amount'], data['date'], data['description'])
        self.clear_form()
        self.load_transactions()
        self.update_balance()
        self.show_message("Успех", "Транзакция добавлена!")

    def save_transaction(self):
        if not self.editing_transaction_id:
            return
        
        data = self._get_transaction_data()
        if not data:
            return
        
        self.db.update_transaction(self.editing_transaction_id, data['type'], data['category_id'],
                                  data['amount'], data['date'], data['description'])
        self.cancel_edit()
        self.load_transactions()
        self.update_balance()
        self.show_message("Успех", "Транзакция обновлена!")

    def cancel_edit(self):
        self.editing_transaction_id = None
        self.clear_form()
        self.add_button.setEnabled(True)
        self.edit_button.setEnabled(False)
        self.cancel_button.setEnabled(False)

    def edit_selected_transaction(self):
        selected = self.transactions_table.selectedItems()
        if not selected:
            self.show_message("Ошибка", "Выберите транзакцию для редактирования!")
            return

        transaction_id = int(self.transactions_table.item(selected[0].row(), 0).text())
        transactions = self.db.get_transactions(self.user_id)
        transaction = next((t for t in transactions if t[0] == transaction_id), None)
        
        if not transaction:
            return

        self.editing_transaction_id = transaction_id
        trans_id, type_int, category_id, category_name, amount, date_str, description = transaction
        
        self.type_combo.setCurrentText("доход" if type_int == 0 else "расход")
        self.update_categories()
        self.category_combo.setCurrentText(category_name)
        self.amount_input.setText(str(amount))
        self.date_input.setDate(QDate.fromString(date_str, "yyyy-MM-dd"))
        self.description_input.setText(description or "")
        
        self.add_button.setEnabled(False)
        self.edit_button.setEnabled(True)
        self.cancel_button.setEnabled(True)

    def delete_transaction(self):
        selected = self.transactions_table.selectedItems()
        if not selected:
            self.show_message("Ошибка", "Выберите транзакцию для удаления!")
            return

        reply = QMessageBox.question(
            self, "Подтверждение", "Вы уверены, что хотите удалить эту транзакцию?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            transaction_id = int(self.transactions_table.item(selected[0].row(), 0).text())
            self.db.delete_transaction(transaction_id)
            self.load_transactions()
            self.update_balance()
            self.show_message("Успех", "Транзакция удалена!")

    def clear_form(self):
        self.amount_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self.description_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.update_categories()

    def load_transactions(self):
        transaction_type = "расход" if self.expenses_only_checkbox.isChecked() else None
        search_text = self.search_input.text() or None
        transactions = self.db.get_transactions(self.user_id, transaction_type, search_text)

        self.transactions_table.setRowCount(len(transactions))
        for row, (trans_id, type_int, _, category_name, amount, date, description) in enumerate(transactions):
            trans_type = "доход" if type_int == 0 else "расход"
            items = [
                QTableWidgetItem(str(trans_id)),
                QTableWidgetItem(trans_type),
                QTableWidgetItem(category_name),
                QTableWidgetItem(f"{amount:.2f}"),
                QTableWidgetItem(date),
                QTableWidgetItem(description or "")
            ]
            for col, item in enumerate(items):
                self.transactions_table.setItem(row, col, item)
            
            color = Qt.GlobalColor.green if type_int == 0 else Qt.GlobalColor.red
            self.transactions_table.item(row, 3).setForeground(color)

    def update_balance(self):
        balance, income, expense = self.db.get_balance(self.user_id)
        self.balance_label.setText(f"Баланс: {balance:.2f} ₽")
        self.income_label.setText(f"Доходы: {income:.2f} ₽")
        self.expense_label.setText(f"Расходы: {expense:.2f} ₽")

    def open_statistics(self):
        if hasattr(self, 'statistics_window') and self.statistics_window.isVisible():
            self.statistics_window.load_statistics()
            self.statistics_window.raise_()
            self.statistics_window.activateWindow()
        else:
            self.statistics_window = StatisticsWindow(self.user_id, self.db)
            self.statistics_window.show()

    def show_message(self, title, text):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.exec()

    def closeEvent(self, event):
        self.db.close()
        event.accept()
