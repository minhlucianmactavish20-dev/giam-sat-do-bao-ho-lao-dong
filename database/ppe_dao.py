from database.db_manager import DatabaseManager
from datetime import datetime, date


class PPEDAO:
    """Data Access Object thao tác dữ liệu nhật ký vi phạm bảo hộ."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def log_violation(self, missing_items, compliance_score, snapshot_path=''):
        """Ghi nhận một trường hợp vi phạm an toàn lao động."""
        now = datetime.now()
        current_date = now.strftime('%Y-%m-%d')
        current_time = now.strftime('%H:%M:%S')

        items_str = ", ".join(missing_items) if isinstance(missing_items, (list, tuple)) else str(missing_items)

        conn = self.db.get_connection()
        try:
            conn.execute(
                '''INSERT INTO violations (date, time, missing_items, compliance_score, snapshot_path)
                   VALUES (?, ?, ?, ?, ?)''',
                (current_date, current_time, items_str, compliance_score, snapshot_path)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Lỗi lưu nhật ký vi phạm: {e}")
            return False
        finally:
            conn.close()

    def get_violations_today(self):
        """Lấy danh sách vi phạm hôm nay."""
        today = date.today().isoformat()
        return self.get_violations_by_date(today)

    def get_violations_by_date(self, target_date):
        """Lấy danh sách vi phạm theo ngày."""
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(
                'SELECT * FROM violations WHERE date = ? ORDER BY id DESC',
                (target_date,)
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_all_violations(self):
        """Lấy tất cả vi phạm."""
        conn = self.db.get_connection()
        try:
            cursor = conn.execute('SELECT * FROM violations ORDER BY id DESC')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_statistics(self, target_date=None):
        """Lấy thống kê số lượt vi phạm."""
        if target_date is None:
            target_date = date.today().isoformat()

        conn = self.db.get_connection()
        try:
            cursor = conn.execute(
                'SELECT COUNT(*) as count FROM violations WHERE date = ?',
                (target_date,)
            )
            count = cursor.fetchone()['count']

            cursor_total = conn.execute('SELECT COUNT(*) as total FROM violations')
            total = cursor_total.fetchone()['total']

            return {
                'date': target_date,
                'violations_today': count,
                'total_violations_all_time': total
            }
        finally:
            conn.close()
