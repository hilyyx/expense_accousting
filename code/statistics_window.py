from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
from PyQt6.QtCore import Qt
from datetime import datetime
from code.resource_path import get_base_dir
import os


class StatisticsWindow(QWidget):
    def __init__(self, user_id, database):
        super().__init__()
        self.user_id = user_id
        self.db = database
        
        self.setWindowTitle("Статистика расходов")
        self.setGeometry(300, 200, 900, 700)
        self.setStyleSheet("background-color: #D3D3D3; color: black;")
        
        self.init_ui()
        self.load_statistics()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        title_label = QLabel("Статистика расходов")
        title_label.setStyleSheet("color: black; padding: 5px;")
        main_layout.addWidget(title_label)

        self.table1 = QTableWidget()
        self.table1.setColumnCount(2)
        self.table1.setHorizontalHeaderLabels(["Категория", "Сумма"])
        self.table1.setStyleSheet("background-color: white; color: black;")
        self.table1.horizontalHeader().setStyleSheet("background-color: #E0E0E0; color: black;")
        self.table1.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table1.setSortingEnabled(True)
        self.table1.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.table1)

        self.total = QLabel("Итого: 0.00 ₽")
        self.total.setStyleSheet("color: black; padding: 5px; background-color: white;")
        main_layout.addWidget(self.total)

        btn_row = QHBoxLayout()
        btn_style = "background-color: white; color: black; padding: 5px;"
        
        btn_export = QPushButton("Экспорт")
        btn_export.setStyleSheet(btn_style)
        btn_export.clicked.connect(self.export_report)
        btn_row.addWidget(btn_export)
        
        main_layout.addLayout(btn_row)
    
    def load_statistics(self):
        self.table1.setSortingEnabled(False)
        data = self.db.get_statistics_by_category(self.user_id, "расход")
        self.table1.setRowCount(len(data))

        sum_total = 0.0
        for i, (cat, summa) in enumerate(data):
            self.table1.setItem(i, 0, QTableWidgetItem(str(cat)))
            self.table1.setItem(i, 1, QTableWidgetItem(f"{float(summa):.2f} ₽"))
            sum_total += float(summa)

        self.total.setText(f"Итого расходов: {sum_total:.2f} ₽")
        self.table1.setSortingEnabled(True)
    
    def export_report(self):
        stat_data = self.db.get_statistics_by_category(self.user_id, "расход")
        bal, income, expense = self.db.get_balance(self.user_id)
        trans_list = self.db.get_transactions(self.user_id)

        report_text = [
            "=" * 50,
            "ОТЧЁТ О РАСХОДАХ",
            "=" * 50,
            f"Дата формирования: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "СТАТИСТИКА ПО КАТЕГОРИЯМ:",
            "-" * 50
        ]

        total_exp = sum(summ for _, summ in stat_data)
        for cat, summ in stat_data:
            report_text.append(f"{cat:30s} {summ:>15.2f} ₽")

        report_text.extend([
            "-" * 50,
            f"{'Итого расходов:':30s} {total_exp:>15.2f} ₽",
            "",
            "ОБЩАЯ СТАТИСТИКА:",
            "-" * 50,
            f"Доходы:     {income:>15.2f} ₽",
            f"Расходы:    {expense:>15.2f} ₽",
            f"Баланс:     {bal:>15.2f} ₽",
            "",
            "ДЕТАЛЬНЫЙ СПИСОК ТРАНЗАКЦИЙ:",
            "-" * 50
        ])

        for t_id, t_type, cat_id, cat_name, summ, dt, desc_text in trans_list:
            type_str = "доход" if t_type == 0 else "расход"
            desc = desc_text or " "
            report_text.append(f"{dt} | {type_str:8s} | {cat_name:15s} | {summ:>10.2f} ₽ | {desc}")

        report_text.append("=" * 50)

        report_path = os.path.join(get_base_dir(), "report.txt")
        with open(report_path, "w", encoding="utf-8") as file:
            file.write("\n".join(report_text))

        self.show_message("Успех", f"Отчёт сохранён в файл report.txt\n\nВсего транзакций: {len(trans_list)}")
    
    def show_message(self, title, text):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.exec()
