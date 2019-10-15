import mysql.connector
try:
  mydb = mysql.connector.connect(
    host="35.197.114.14",
    user="root",
    passwd="gedion"
  )
except Exception as e:
  print(e)

