import ast
import os
import re
import sys
import pymysql
import weaviate
import warnings

from sentence_transformers import SentenceTransformer

warnings.filterwarnings("ignore", category=ResourceWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import a5_Prompt_works.main as a11
import a00_model.main2 as a2

# from a5_Prompt_works.main1 import generate_sql_from_question  # 导入main函数

# 错误定位器
def check_syntax1(cursor, sql_query, Professional_vocabulary, user_question, user_question_type, class_names, similar_records):
    try:
        cursor.execute(sql_query)
        prompt_t = f"""
            您是一位sql语义检查专家，请检查sql：{sql_query}；
            请一句句解释sql，根据以下用户问题和数据库结构来检查SQL是否有语义错误
            用户问题：{user_question}；
            数据库结构：{class_names}；
            请按照以下固定的格式输出：如果发现语义错误请总结错误：语义错误=哪里错了。如果没有发现语义错误请输出：语义错误=未发现 SQL 语义错误
            例如：语义错误=用户问题是查找李梦同学，但是sql是查找李强同学
                 语义错误=未发现 SQL 语义错误
           """
        # 获取SQL响应
        zhipu_AI_out =a2.deepseek_chat_1(prompt_t)
        print("错误定位器的模型返回的语义检查结果：")
        print(zhipu_AI_out)
        print("-------------------------------------------------------")

        result = extract_sql_error(zhipu_AI_out)

        if result != "":  # 如果有错误
            print("错误定位器的得到语义错误的结果：" + result)
            if "未发现 SQL 语义错误" in result:
                # 优化器建议
                i=1
                optimized_sql = Suggestion_optimizer(cursor, sql_query, user_question, class_names,i)
                print("优化后的 SQL: ", optimized_sql)
                return "对的"+optimized_sql  # 返回优化后的 SQL
            else:
                # 进行修复
                error_information = "SQL 语义错误:" + result
                sql_query1 = repair_program(cursor, sql_query, error_information, Professional_vocabulary, user_question,
                                           user_question_type, class_names, similar_records)
                return check_syntax1(cursor, sql_query1, Professional_vocabulary, user_question, user_question_type, class_names, similar_records)
        else:
            return "对的"+sql_query  # 如果没有语义错误，返回原始 SQL
    except pymysql.MySQLError as e:
        error_information = "SQL 语法错误:" + str(e)
        print("错误定位器的得到语法错误的结果：" + str(e))
        sql_query1 = repair_program(cursor, sql_query, error_information, Professional_vocabulary, user_question,
                                   user_question_type, class_names, similar_records)
        return "错的"+sql_query1  # 返回修复后的 SQL



def repair_program(cursor,sql_query,error_information,Professional_vocabulary, user_question, user_question_type, class_names, similar_records):
    """修复一些常见的 SQL 错误"""
    # 生成SQL提示
    prompt_t = f"""
        你是一个用户问题多样化专家。根据给定的用户问题，生成多个表达方式相似但用词和句型不同的版本。确保每个版本都是清晰且能够被理解的。以下是用户问题：
        {user_question}
        请把多样化后的结果用数组的形式输出
        例如：用户问题：获取“material_appropriation”表中所有类型为“领用”的记录。
             输出结果：
            user_questions=["获取 `material_appropriation` 表中所有类型为‘领用’的记录。",
            "从 `material_appropriation` 表中筛选出所有类型为‘领用’的记录。",
            "请查询 `material_appropriation` 表中所有类型为‘领用’的条目。",
            "能否列出 `material_appropriation` 表中所有类型为‘领用’的记录？",
            "请提供 `material_appropriation` 表中所有类型为‘领用’的记录。"]
    """
    # 获取SQL响应
    user_question_duo = a2.deepseek_chat_2(prompt_t)
    print("-------------------------------------------------------")
    print("多样化用户问题的模型返回的语义检查结果：")
    print(user_question_duo)
    print("-------------------------------------------------------")
    user_question_duo=extract_user_questions(user_question_duo)
    prompt_t = f"""
        假设您是油田领域的text-to-sql专家，请帮我根据以下信息生成五个用户问题对应的SQL。
        用户问题：{user_question_duo}；
        错误SQL：{sql_query},{error_information}
        相关术语：{Professional_vocabulary}；
        用户问题查询类型：{user_question_type}；
        数据库结构：{class_names}；
        相似示例：{similar_records}；
        请把生成结果用双层数组的形式输出，请输出每个用户问题对应的SQL
        例如：用户问题：获取“material_appropriation”表中所有类型为“领用”的记录。
             输出结果：
                sql_statements =[
                    [
                        "获取 `material_appropriation` 表中所有类型为‘领用’的记录。",
                        "SELECT * FROM material_appropriation WHERE type = '领用';"
                    ],
                    [
                        "从 `material_appropriation` 表中筛选出所有类型为‘领用’的记录。",
                        "SELECT * FROM material_appropriation WHERE type = '领用';"
                    ],
                    [
                        "请查询 `material_appropriation` 表中所有类型为‘领用’的条目。",
                        "SELECT * FROM material_appropriation WHERE type = '领用';"
                    ],
                    [
                        "能否列出 `material_appropriation` 表中所有类型为‘领用’的记录？",
                        "SELECT * FROM material_appropriation WHERE type = '领用';"
                    ],
                    [
                        "请提供 `material_appropriation` 表中所有类型为‘领用’的记录。",
                        "SELECT * FROM material_appropriation WHERE type = '领用';"
                    ]
                ]
    """
    # 获取SQL响应
    sql_query = a2.deepseek_chat_22(prompt_t)
    print("-------------------------------------------------------")
    print("多样化用户问题后得到对应的SQL的模型返回的语义检查结果：")
    print(sql_query)
    print("-------------------------------------------------------")
    Candidate_result=extract_sql_statements_from_input(sql_query)
    return Repair_serum(cursor,Candidate_result,Professional_vocabulary, user_question, user_question_type, class_names, similar_records)

# 修复精华器
def Repair_serum(cursor,Candidate_result,Professional_vocabulary, user_question, user_question_type, class_names, similar_records):
    prompt_t = f"""
        假设您是油田领域的text-to-sql专家，请根据以下信息帮我从候选用户问题和sql选择一条最正确的sql。
        请一定要从候选用户问题和sql中选择一条。
        请一定要从候选用户问题和sql中选择一条。
        请一定要从候选用户问题和sql中选择一条。
        注意表和列都用英文
        候选用户问题和sql：{Candidate_result}；
        用户问题：{user_question}；
        数据库结构：{class_names}；
        请按照以下格式输出：sql=''
    """
    # 获取SQL响应
    sql_query=a2.deepseek_chat_2(prompt_t)
    print("-------------------------------------------------------")
    print("修复精华器的模型返回的语义检查结果：")
    print(sql_query)
    print("-------------------------------------------------------")
    sql_query = extract_sql_query(sql_query)
    print("修复精华器的模型得到的SQL：")
    print(sql_query)
    print("-------------------------------------------------------")
    return sql_query

# 建议优化器
def Suggestion_optimizer(cursor, sql_query, user_question, class_names,i):
    print("sql_query", sql_query)
    cursor.execute(sql_query)
    results = cursor.fetchall()
    print("results", results)
    prompt_t = f"""
        假设您是油田领域的text-to-sql专家，以下sql是正确的，请帮我把以下sql进行语法优化。
        用户问题：{user_question}；
        生成的sql：{sql_query}；
        数据库结构：{class_names}；
        请按照以下格式输出：sql=''
        请不要输出其他信息，请只输出sql=''
    """

    # 获取SQL响应
    sql_query11 = a2.deepseek_chat_4(prompt_t)
    print("-------------------------------------------------------")
    print("建议优化器的模型返回的语义检查结果：")
    print(sql_query11)
    print("-------------------------------------------------------")

    # 提取优化后的 SQL
    sql_query1 = extract_sql_query(sql_query11)
    print("优化后得到的sql_query", sql_query1)
    try:
        # 执行优化后的 SQL 并获取结果
        cursor.execute(sql_query1)
        results1 = cursor.fetchall()
        # 如果优化后的 SQL 与原 SQL 结果相同，返回优化后的 SQL
        if results and results1 and results == results1:
            print("优化后的 SQL 与原 SQL 结果相同")
            return sql_query1  # 返回优化后的 SQL
        else:
            print("优化后的 SQL 与原 SQL 结果不同，继续优化...")
            # return sql_query  # 返回原 SQL
            ii=1+i
            if ii==3:
                return sql_query
            return Suggestion_optimizer(cursor, sql_query, user_question, class_names,ii)
    except pymysql.MySQLError as e:
            # return sql_query  # 返回原 SQL
        ii=1+i
        if ii==3:
            return sql_query
        return Suggestion_optimizer(cursor, sql_query, user_question, class_names,ii)


def extract_sql_error(zhipu_AI_out):
    """
    从模型输出中提取 SQL 语义错误信息。
    :param zhipu_AI_out: 模型返回的输出字符串
    :return: 如果包含 SQL 语义错误，则返回错误信息，否则返回提示信息
    """
    if "语义错误=" in zhipu_AI_out:
        # 提取 'SQL 语义错误:' 后面的内容
        error_message = zhipu_AI_out.split("语义错误=")[1].strip()
        return error_message
    elif "语义错误:" in zhipu_AI_out:
        # 提取 '语义错误:' 后面的内容
        error_message = zhipu_AI_out.split("语义错误:")[1].strip()
        return error_message
    else:
        return ""  # 如果没有找到语义错误


def extract_sql_query(sql_query):
    """
    从给定的 SQL 查询字符串中提取纯 SQL 语句部分。
    :param sql_query: 包含完整 SQL 查询的字符串
    :return: 提取出的 SQL 语句，如果未找到则返回空字符串
    """
    sql_only = ''
    # 去除多余的前后空格和换行符，提取出包含 sql= 语句的部分
    sql_query = sql_query.strip()  # 去除字符串首尾的空白字符
    # 使用正则表达式提取 sql=' 和最后一个 ' 之间的部分
    match = re.search(r"sql='(.*)'", sql_query.strip(), re.DOTALL)
    if match:
        sql_only = match.group(1).strip()  # 提取 sql=' 后到最后一个 ' 之间的内容
        # 修复单引号转义问题
        sql_only = sql_only.replace("''", "'")
        sql_only = sql_only.replace("\\", "")
        sql_only = sql_only.replace('"', "'")
        sql_only = sql_only.replace(";'", "")
        print("提取的 SQL 查询:", sql_only)
        return sql_only
    else:
        print("未能提取出 SQL 查询")

    return sql_only
def extract_user_questions(user_questions_string):
    """
    从给定的字符串中提取用户问题列表。
    :param user_questions_string: 包含用户问题的字符串
    :return: 返回解析后的用户问题列表，或返回错误信息
    """
    try:
        # 提取等号后面的内容并解析为 Python 列表
        user_questions = ast.literal_eval(user_questions_string.split('=')[1].strip())
        return user_questions
    except Exception as e:
        return f"user_questions解析失败: {e}"


def extract_sql_statements_from_input(input_str):
    """
    从给定的字符串中提取出 SQL 查询部分（sql_statements）。
    :param input_str: 输入的字符串，包含 user_questions 和 sql_statements。
    :return: 提取出的 SQL 查询列表
    """
    # 使用 ast.literal_eval 来安全地解析 Python 字符串中的字面量列表
    try:
        # 从输入字符串中提取出 sql_statements 部分
        start_index = input_str.index("sql_statements =") + len("sql_statements =")
        end_index = input_str.index("user_question =", start_index)  # 假设 user_question 后在 sql_statements 之后
        sql_statements_str = input_str[start_index:end_index].strip()

        # 使用 ast.literal_eval 来解析 SQL 语句列表
        sql_statements = ast.literal_eval(sql_statements_str)

        # 提取 SQL 查询语句部分
        sql_queries = [statement[1] for statement in sql_statements]

        return sql_queries
    except Exception as e:
        return f"sql_statements解析失败: {e}"



# # sql生成真的
# user_question = "找出“material_appropriation”表中所有申请人是王强的记录"
# #sql假的
# sql_query="SELECT * FROM material_appropriation WHERE type = '王强'"
# Professional_vocabulary=""
# user_question_type="简单查询"
# class_names="material_appropriation"
# similar_records=""
# client = weaviate.Client("http://localhost:8080")
# user_question = "获取“material_appropriation”表中所有类型为“领用”的记录。"
# model = SentenceTransformer('D:/my_langchain/myProject1/text2vec-base-chinese')
# sql_query,Professional_vocabulary, user_question, user_question_type, class_names, similar_records = a11.generate_sql_model2(user_question,model,client)
# print("生成的 SQL 查询:", sql_query)
# sql_query =extract_sql_query(sql_query)
# # 构建假的
# # 连接到 MySQL 数据库
#
#
# connection = pymysql.connect(
#     host='localhost', user='root', password='123456', database='lhr', charset='utf8mb4'
# )
# cursor = connection.cursor()
#
# final_sql1 = check_syntax1(cursor, sql_query, Professional_vocabulary, user_question, user_question_type, class_names, similar_records)
# final_sql = ""
# # 第一次检查，假设 final_sql1 已经有值
# if final_sql1[:2] == '对的':
#     final_sql = final_sql1[2:]
# elif final_sql1[:2] == '错的':
#     # 第一次调用 check_syntax
#     final_sql2 = final_sql1[2:]
#     final_sql2 = check_syntax1(cursor, final_sql2, Professional_vocabulary, user_question, user_question_type, class_names, similar_records)
#     # 第二次检查
#     if final_sql2[:2] == '对的':
#         final_sql = final_sql2[2:]
#     elif final_sql2[:2] == '错的':
#         # 第三次调用 check_syntax
#         final_sql3 = final_sql2[2:]
#         final_sql3 = check_syntax1(cursor, final_sql3, Professional_vocabulary, user_question, user_question_type, class_names, similar_records)
#         if final_sql3[:2] == '对的':
#             final_sql = final_sql3[2:]
#         elif final_sql3[:2] == '错的':
#             final_sql = final_sql3[2:]
#
# print(final_sql)
# cursor.close()  # 关闭游标
# connection.close()  # 关闭数据库连接


def generate_sql_and_check2(user_question, model, client, cursor):
    """生成并检查 SQL 查询"""
    # 生成SQL查询
    sql_query, Professional_vocabulary, user_question, user_question_type, class_names, similar_records = a11.generate_sql_model2(user_question, model, client)
    sql_query = extract_sql_query(sql_query)
    print("初步生成的 SQL 查询:", sql_query)

    # 第一次检查
    final_sql1 = check_syntax1(cursor, sql_query, Professional_vocabulary, user_question, user_question_type, class_names, similar_records)
    final_sql = ""

    if final_sql1[:2] == '对的':
        # final_sql = final_sql1[2:]
        final_sql = final_sql1
    elif final_sql1[:2] == '错的':
        # 第二次检查
        # final_sql2 = final_sql1[2:]
        final_sql = final_sql1
        final_sql2 = check_syntax1(cursor, final_sql1[2:], Professional_vocabulary, user_question, user_question_type, class_names, similar_records)

        if final_sql2[:2] == '对的':
            final_sql = final_sql2
            # final_sql = final_sql2[2:]
        elif final_sql2[:2] == '错的':
            # 第三次检查
            final_sql = final_sql2
            # final_sql3 = final_sql2[2:]
            final_sql3 = check_syntax1(cursor, final_sql2[2:], Professional_vocabulary, user_question, user_question_type, class_names, similar_records)
            if final_sql3[:2] == '对的':
                final_sql = final_sql3
                # final_sql = final_sql3[2:]
            elif final_sql3[:2] == '错的':
                final_sql = final_sql3
                # final_sql = final_sql3[2:]
    a2.get_result1(final_sql)
    return final_sql,sql_query, Professional_vocabulary, user_question, user_question_type, class_names, similar_records




# connection = pymysql.connect(
#     host='localhost', user='root', password='123456', database='lhr', charset='utf8mb4'
# )
# cursor = connection.cursor()
# client = weaviate.Client("http://localhost:8080")
# user_question = "获取“material_appropriation”表中所有类型为“领用”的记录。"
# model = SentenceTransformer('D:/my_langchain/myProject1/text2vec-base-chinese')
# a=generate_sql_and_check(user_question, model, client, cursor)
# print(a)
# # 关闭数据库连接
# cursor.close()
# connection.close()


