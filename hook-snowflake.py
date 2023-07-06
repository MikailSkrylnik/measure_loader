# hook-snowflake.py
# snow_logging is mandatory to get arrow working

hiddenimports = ["snowflake.connector.snow_logging"]

from PyInstaller.utils.hooks  import  copy_metadata

datas = []

datas.append(copy_metadata('snowflake-connector-python')[0])