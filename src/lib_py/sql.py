import sqlite3
import uuid

class Database:
    def __init__(self, db_name='permissions.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            uuid TEXT PRIMARY KEY
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS permissions (
            permission_id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_permissions (
            uuid TEXT,
            permission_id INTEGER,
            FOREIGN KEY (uuid) REFERENCES users (uuid),
            FOREIGN KEY (permission_id) REFERENCES permissions (permission_id),
            PRIMARY KEY (uuid, permission_id)
        )
        ''')
        self.conn.commit()
    
    def close(self):
        self.conn.close()

class User:
    def __init__(self, db):
        self.db = db
    
    def add_user(self):
        user_uuid = str(uuid.uuid4())
        self.db.cursor.execute('INSERT INTO users (uuid) VALUES (?)', (user_uuid,))
        self.db.conn.commit()
        return user_uuid

class Permission:
    def __init__(self, db):
        self.db = db
    
    def add_permission(self, action):
        self.db.cursor.execute('INSERT INTO permissions (action) VALUES (?)', (action,))
        self.db.conn.commit()
        return self.db.cursor.lastrowid
    
    def assign_permission(self, user_uuid, permission_id):
        self.db.cursor.execute('INSERT INTO user_permissions (uuid, permission_id) VALUES (?, ?)', (user_uuid, permission_id))
        self.db.conn.commit()

class UserPermissions:
    def __init__(self, db):
        self.db = db
    
    def get_user_permissions(self, user_uuid):
        self.db.cursor.execute('''
        SELECT permissions.action
        FROM user_permissions
        JOIN permissions ON user_permissions.permission_id = permissions.permission_id
        WHERE user_permissions.uuid = ?
        ''', (user_uuid,))
        return self.db.cursor.fetchall()

class AccessControl:
    def __init__(self, db):
        self.db = db

    def check_permission(self, user_uuid, action):
        self.db.cursor.execute('''
        SELECT 1
        FROM user_permissions
        JOIN permissions ON user_permissions.permission_id = permissions.permission_id
        WHERE user_permissions.uuid = ? AND permissions.action = ?
        ''', (user_uuid, action))
        return self.db.cursor.fetchone() is not None

# 使用範例
if __name__ == "__main__":
    db = Database()
    
    user_obj = User(db)
    permission_obj = Permission(db)
    user_permissions_obj = UserPermissions(db)
    access_control = AccessControl(db)
    
    # 添加一個新用戶
    user_uuid = user_obj.add_user()
    print(f'New user UUID: {user_uuid}')
    
    # 添加一些權限
    read_permission_id = permission_obj.add_permission('read')
    write_permission_id = permission_obj.add_permission('write')
    print(f'Added permissions with IDs: {read_permission_id}, {write_permission_id}')
    
    # 分配權限給用戶
    permission_obj.assign_permission(user_uuid, read_permission_id)
    permission_obj.assign_permission(user_uuid, write_permission_id)
    
    # 查詢用戶的權限
    user_permissions = user_permissions_obj.get_user_permissions(user_uuid)
    print(f'Permissions for user {user_uuid}: {user_permissions}')
    
    # 檢查用戶權限
    can_read = access_control.check_permission(user_uuid, 'read')
    can_write = access_control.check_permission(user_uuid, 'write')
    print(f'User {user_uuid} can read: {can_read}')
    print(f'User {user_uuid} can write: {can_write}')
    
    # 嘗試使用控制項
    if access_control.check_permission(user_uuid, 'read'):
        print('Access granted for reading.')
    else:
        print('Access denied for reading.')

    if access_control.check_permission(user_uuid, 'write'):
        print('Access granted for writing.')
    else:
        print('Access denied for writing.')
    
    # 關閉資料庫連接
    db.close()
