import sqlite3
import os


class Database:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.normpath(os.path.join(base_dir, "..", "database", "database.db"))
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
    
    def register_user(self, username, password):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            self.conn.commit()
            return True, None
        except sqlite3.IntegrityError:
            return False, "Пользователь с таким именем уже существует."
        except Exception as e:
            return False, str(e)
    
    def login_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        return (True, user[0]) if user else (False, None)
    
    def add_transaction(self, user_id, transaction_type, category_id, amount, date, description):
        cursor = self.conn.cursor()
        type_int = 0 if transaction_type == "доход" else 1
        cursor.execute("""
            INSERT INTO transactions (user_id, category_id, type, amount, date, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, category_id, type_int, amount, date, description))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_transactions(self, user_id, transaction_type=None, search_text=None):
        cursor = self.conn.cursor()
        query = """
            SELECT t.id, t.type, t.category_id, c.name as category_name, t.amount, t.date, t.description 
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id=?
        """
        params = [user_id]
        
        if transaction_type: #сортировка только расход
            query += " AND t.type=?"
            params.append(0 if transaction_type == "доход" else 1)
        if search_text: #ПОИСК ПО ОПИСАНИЮ
            query += " AND t.description LIKE ?"
            params.append(f"%{search_text}%")
        
        cursor.execute(query + " ORDER BY t.date DESC", params)
        return cursor.fetchall()
    
    def update_transaction(self, transaction_id, transaction_type, category_id, amount, date, description):
        cursor = self.conn.cursor()
        type_int = 0 if transaction_type == "доход" else 1
        cursor.execute("""
            UPDATE transactions 
            SET type=?, category_id=?, amount=?, date=?, description=?
            WHERE id=?
        """, (type_int, category_id, amount, date, description, transaction_id))
        self.conn.commit()
    
    def delete_transaction(self, transaction_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
        self.conn.commit()
    
    def get_balance(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_id=? AND type=?", (user_id, 0))
        income = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_id=? AND type=?", (user_id, 1))
        expense = cursor.fetchone()[0] or 0
        return income - expense, income, expense
    
    def get_statistics_by_category(self, user_id, transaction_type="расход"):
        cursor = self.conn.cursor()
        type_int = 0 if transaction_type == "доход" else 1
        cursor.execute("""
            SELECT categories.name, SUM(transactions.amount) as total
            FROM transactions
            INNER JOIN categories ON transactions.category_id = categories.id
            WHERE transactions.user_id = ? AND transactions.type = ?
            GROUP BY categories.name 
            ORDER BY total DESC
        """, (user_id, type_int))
        return cursor.fetchall()

    def get_categories(self, user_id, category_type=None):
        cursor = self.conn.cursor()
        if category_type is not None:
            cursor.execute("SELECT id, name, type FROM categories WHERE user_id=? AND type=? ORDER BY name", 
                         (user_id, category_type))
        else:
            cursor.execute("SELECT id, name, type FROM categories WHERE user_id=? ORDER BY type, name", (user_id,))
        return cursor.fetchall()
    
    def add_category(self, user_id, category_type, category_name):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO categories (name, type, user_id) VALUES (?, ?, ?)",
                      (category_name, category_type, user_id))
        self.conn.commit()
        return True, cursor.lastrowid

    def get_default_categories(self, user_id):
        if self.get_categories(user_id):
            return
        defaults = [
            ("Зарплата", 0), ("Подарки", 0), ("Инвестиции", 0), ("Прочее", 0),
            ("Еда", 1), ("Транспорт", 1), ("Жилье", 1), ("Здоровье", 1), ("Учеба", 1), ("Прочее", 1)
        ]
        for name, typee in defaults:
            self.add_category(user_id, typee, name)
    
    def close(self):
        self.conn.close()
