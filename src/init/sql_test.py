import sqlite3
import uuid

class Database:
    # 創建數據庫
    def __init__(self, db_name='lego_dataset.db'):
        self.conn = sqlite3.connect(db_name)
        # 啟用游標
        self.cursor = self.conn.cursor()
        self.create_tables()

    # 新增資料表
    def create_tables(self):
        # users
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            in_date TIMESTAMP
        )''')
        # permissions
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS permissions (
            permission_id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL
        )''')
        # user_permissions
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_permissions (
            user_id TEXT,
            permission_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (permission_id) REFERENCES permissions (permission_id),
            PRIMARY KEY (user_id, permission_id)
        )''')
        # script
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS script (
            script_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brick_path TEXT NOT NULL
        )''')
        # model
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS model (
            model_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            model_path TEXT NOT NULL,
            parameter INTEGER NOT NULL
        )''')
        # practice
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS practice (
            practice_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            script_id INTEGER NOT NULL, 
            user_id TEXT NOT NULL,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            score INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (script_id) REFERENCES script (script_id)
        )''')
        self.conn.commit()

    # 刪除資料表
    def drop_table(self, table_name):
        self.cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
        self.conn.commit()

    # 修改資料表內容
    def update_data(self, table_name, set_clause, condition, values):
        query = f'UPDATE {table_name} SET {set_clause} WHERE {condition}'
        self.cursor.execute(query, values)
        self.conn.commit()

    # 刪除資料表內容
    def delete_data(self, table_name, condition, value):
        query = f'DELETE FROM {table_name} WHERE {condition}=?'
        self.cursor.execute(query, (value,))
        self.conn.commit()

    # 關閉資料庫連接
    def close(self):
        self.conn.close()

# 新增users资料
class Users:
    def __init__(self, db):
        self.db = db
    # 插入資料
    def add_user(self, user_name, user_email, user_password):
        user_id = str(uuid.uuid4())
        self.db.cursor.execute('''
        INSERT INTO users (user_id, name, email, password, in_date) VALUES (?, ?, ?, ?, datetime('now'))
        ''', (user_id, user_name, user_email, user_password))
        # 提交至SQLite
        self.db.conn.commit()
        return user_id
    # 刪除資料
    def drop_user(self, user_id,user_name, user_email, user_password):
        self.db.cursor.execute('''
        drop INTO users (user_id, name, email, password, in_date) VALUES (?, ?, ?, ?, datetime('now'))
        ''', (user_id, user_name, user_email, user_password))
# 新增Permissions資料
class Permissions:
    def __init__(self, db):
        self.db = db
    # 新增动作
    def add_permission(self, action):
        self.db.cursor.execute('INSERT INTO permissions(action) VALUES(?)', (action,))
        self.db.conn.commit()
        # 獲取主鍵id 值
        return self.db.cursor.lastrowid

# 新增user_permissions資料
class UserPermissions:
    def __init__(self, db):
        self.db = db
    # 分配權限
    def assign_permission(self, user_id, permission_id):
        self.db.cursor.execute('INSERT INTO user_permissions(user_id, permission_id) VALUES (?, ?)', (user_id, permission_id))
        self.db.conn.commit()
    # 查尋用戶ID權限
    def get_user_permissions(self, user_id):
        self.db.cursor.execute('''
        SELECT permissions.action
        FROM user_permissions 
        LEFT JOIN permissions ON user_permissions.permission_id = permissions.permission_id
        WHERE user_permissions.user_id = ?
        ''', (user_id,))
        return self.db.cursor.fetchall()

# 新增script资料
class Script:
    def __init__(self, db):
        self.db = db
    # 插入资料
    def add_script(self, name, brick_path):
        self.db.cursor.execute('''
        INSERT INTO script (name, brick_path) VALUES (?, ?)
        ''', (name, brick_path))
        # 提交至SQLite
        self.db.conn.commit()
        # 获取所插入数据的主键ID值
        return self.db.cursor.lastrowid

# 新增model资料
class Model:
    def __init__(self, db):
        self.db = db
    # 插入资料
    def add_model(self, name, model_path, parameter):
        self.db.cursor.execute('''
        INSERT INTO model (name, model_path, parameter) VALUES (?, ?, ?)
        ''', (name, model_path, parameter))
        # 提交至SQLite
        self.db.conn.commit()
        # 获取所插入数据的主键ID值
        return self.db.cursor.lastrowid

# 新增practice资料
class Practice:
    def __init__(self, db):
        self.db = db
    
    def add_practice(self, project_name, script_id, user_id, start_time, end_time, score):
        self.db.cursor.execute('''
        INSERT INTO practice (project_name, script_id, user_id, start_time, end_time, score) 
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (project_name, script_id, user_id, start_time, end_time, score))
        # 提交至SQLite
        self.db.conn.commit()
        # 获取所插入数据的主键ID值
        return self.db.cursor.lastrowid

