"""
Модуль для правильной работы с путями в собранном .exe
"""
import os
import sys


def resource_path(relative_path):
    """
    Получает правильный путь к ресурсу, работает и в dev, и в PyInstaller
    
    Args:
        relative_path: Относительный путь к ресурсу (например, "res/money_icon.png")
    
    Returns:
        Абсолютный путь к ресурсу
    """
    try:
        # PyInstaller создает временную папку и сохраняет путь в _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Если не в PyInstaller, используем обычный путь
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)


def get_base_dir():
    """
    Получает базовую директорию приложения (где находится .exe или скрипт)
    
    Returns:
        Путь к директории приложения
    """
    if getattr(sys, 'frozen', False):
        # Если приложение собрано в .exe
        return os.path.dirname(sys.executable)
    else:
        # Если запущено как скрипт
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_database_path():
    """
    Получает путь к базе данных (создается рядом с .exe)
    
    Returns:
        Путь к файлу базы данных
    """
    base_dir = get_base_dir()
    db_dir = os.path.join(base_dir, "database")
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "database.db")

