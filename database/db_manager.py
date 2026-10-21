import sqlite3
import os
from config import DB_PATH


class DatabaseManager:
    """Quản lý kết nối & Khởi tạo CSDL SQLite cho Nhật ký vi phạm an toàn."""

    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH
        self._init_database()

    def _init_database(self):
        """Tạo bảng violations nếu chưa tồn tại."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                missing_items TEXT NOT NULL,
                compliance_score REAL NOT NULL,
                snapshot_path TEXT DEFAULT ''
            )
        ''')

        conn.commit()
        conn.close()

    def get_connection(self):
        """Lấy kết nối tới SQLite database."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
