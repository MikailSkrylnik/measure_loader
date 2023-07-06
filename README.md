# Measure Loader
![Static Badge](https://img.shields.io/badge/python--dotenv-1.0.0-blue) 
![Static Badge](https://img.shields.io/badge/snowflake--connector--python-3.0.4-blue)
![Static Badge](https://img.shields.io/badge/pyinstaller-5.13.0-blue) 
![Static Badge](https://img.shields.io/badge/pyarrow-12.0.1-blue) 

## Define .env
Create your .env file in the following format:
```env
USER=
PASSWORD=
ACCOUNT=
WAREHOUSE=
DATABASE=
SCHEMA=
TARGET_TABLE=
```

## Launch build.bat
It will generate an .exe file with the program in 
> dist/main.exe

## Describe the measures in PBI file
Script will automatically select measures with descriptions to be loaded into snowflake, so it is recommended to describe measures into PBI files itself instead of measure export tool as this way you would only need to do it once.
To describe the measure in PowerBI you should open Tabular Editor (external tool), select measure, find in category "Basic" option "Description" and leave a comment here.
When you open a script later you will see green lines for measures with comments and last column "Load" will have value "True", which means that it will be loaded to Snowflake.
All you need to do now is to check that all measures you would like to export are included (if they are not, change comment manually and click on "False" in "Load" column) and click "Load to Snowflake"

![image](https://github.com/MikailSkrylnik/measures_extraction/assets/99406877/c6d72f01-2268-4309-b1a6-1831f2eb54d1)
