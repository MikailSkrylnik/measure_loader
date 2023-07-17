import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Snowflake connection details
snowflake_config = {
    'user': os.getenv('USER'),
    'password': os.getenv('PASSWORD'),
    'account': os.getenv('ACCOUNT'),
    'warehouse': os.getenv('WAREHOUSE'),
    'database': os.getenv('DATABASE'),
    'schema': os.getenv('SCHEMA'),
    'target_table': os.getenv('TARGET_TABLE')
}

src = open('main.py', 'r')
lines = src.readlines()
dst = open('main.py', 'w')

lines[11] = f"snowflake_config = {{ 'user': '{snowflake_config['user']}', 'password': '{snowflake_config['password']}', 'account': '{snowflake_config['account']}', 'warehouse': '{snowflake_config['warehouse']}', 'database': '{snowflake_config['database']}', 'schema': '{snowflake_config['schema']}', 'target_table': '{snowflake_config['target_table']}' }}\n"
dst.writelines(lines)

src.close()
dst.close()
