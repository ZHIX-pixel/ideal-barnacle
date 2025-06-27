import os
import sys
import pymysql
def generate_sql_model55(cursor,sql_query):
    try:
        # # 连接数据库
        # connection = pymysql.connect(
        #     host='localhost', user='root', password='123456', database='lhr', charset='utf8mb4',
        #     cursorclass=pymysql.cursors.DictCursor
        # )
        # cursor = connection.cursor()
        # 执行 SQL 查询
        cursor.execute(sql_query)
        # 获取结果
        user = cursor.fetchone()


        return "正确"  # 返回查询结果
    except Exception as e:
        # 捕获异常并返回错误信息
        error_message = f"执行 SQL 查询时发生错误：{e}"
        return error_message

# print(generate_sql_model55("SELECT * FROM material_appropriation WHERE type = '领用';"))