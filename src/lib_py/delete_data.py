
from sql_test import Database

# Initialize the database
db = Database()

# Define the table name, condition, and value
table_name = 'model'
condition = 'name'
value = 'Model A'

# Call the delete_data method
db.delete_data(table_name, condition, value)

# Close the database connection
db.close()
print('ok')