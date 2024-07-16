from sql_test import Database, Users,Permissions,UserPermissions,Script,Model,Practice

# 使用示例
db = Database()
users_manager = Users(db)
permissions_manager = Permissions(db)
user_permissions_manager = UserPermissions(db)
script_manager = Script(db)
model_manager = Model(db)
practice_manager = Practice(db)

# 新增用户
new_user_id = users_manager.add_user('Tim', 'Tim@example.com', 'password456')
print(f'New user ID: {new_user_id}')

# 新增權限
new_permission_id = permissions_manager.add_permission('write')
print(f'New permission ID: {new_permission_id}')

# 分配權限
user_permissions_manager.assign_permission(new_user_id, new_permission_id)

# 查詢用戶權限
user_permissions = user_permissions_manager.get_user_permissions(new_user_id)
print(f'User permissions: {user_permissions}')

# 新增腳本
new_script_id = script_manager.add_script('Script B', '/path/to/brick/B')
print(f'New script ID: {new_script_id}')

# 新增模型
new_model_id = model_manager.add_model('Model B', '/path/to/model', 456)
print(f'New model ID: {new_model_id}')

# 新增練習紀錄
new_practice_id = practice_manager.add_practice('Project B', new_script_id, new_user_id, '2024-07-16 10:00:00', '2024-07-16 12:00:00', 90)
print(f'New practice ID: {new_practice_id}')
