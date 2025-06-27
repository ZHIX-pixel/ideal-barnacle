import os
import re
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from .修复 import generate_sql_model11
from .候选生成 import generate_sql_model22
from .候选选择 import generate_sql_model33
from .值验证 import generate_sql_model44
from .执行 import generate_sql_model55
from .生成 import generate_sql_model66
from .自检查 import generate_sql_model77
from .语义模型 import generate_sql_model88
from .语义骨架验证 import generate_sql_model99
from .语法 import generate_sql_model100
def all1(cursor,model,client,user_question,model_name,tisi,Professional_vocabulary,similar_records,debug_count,class_names,user_question_type):
    print("生成-执行验证-值验证-语义验证-语法验证-修复-对齐输出")
    print("-----------------------------------------")
    for _ in range(int(debug_count)):  # 根据 debug_count 控制循环次数
        sql = generate_sql_model66(Professional_vocabulary,similar_records,class_names,user_question_type,tisi, user_question, model_name)
        print("sql:::::",sql)
        zhixing = generate_sql_model55(cursor,sql)
        zhiyanzheng = generate_sql_model44(user_question, sql, model_name)
        yuyimoxing = generate_sql_model88(sql, user_question, model_name)
        yufa = generate_sql_model100(sql, model_name)
        print("执行结果：", zhixing)
        print("值验证（验证成功=1,验证失败=0）：", zhiyanzheng)
        print("语义验证（验证成功>0.8,验证失败<0.8）：", float(yuyimoxing))
        print("语法验证(语法修复后的SQL)：", yufa)
        if zhixing == "正确" and zhiyanzheng == "1" and float(yuyimoxing) >= 0.8:
            return "正确"+sql  # 如果所有条件都满足，返回 sql 并结束循环
        sql = yufa
        result = (
            "执行结果：" + zhixing +
            "。值验证（验证成功=1,验证失败=0）：" + zhiyanzheng +
            "。语义验证（验证成功>0.8,验证失败<0.8）：" + yuyimoxing +
            "。语法验证(语法修复后的SQL)：" + yufa +
            "。"
        )
        sql_query = generate_sql_model11(Professional_vocabulary,user_question_type,class_names,similar_records,user_question, sql, model, client, model_name, result)
        sql = sql_query
    return "错误"+sql
def all2(model,client,user_question,model_name,tisi,Professional_vocabulary,similar_records,debug_count,class_names,user_question_type):
    print("生成-语义验证-语法验证-修复-对齐输出")
    print("-----------------------------------------")
    for _ in range(int(debug_count)):  # 根据 debug_count 控制循环次数
        sql = generate_sql_model66(Professional_vocabulary,similar_records,class_names,user_question_type,tisi, user_question, model_name)
        print("sql:::::",sql)
        yuyimoxing = generate_sql_model88(sql, user_question, model_name)
        yufa = generate_sql_model100(sql, model_name)
        print("语义验证（验证成功>0.8,验证失败<0.8）：", yuyimoxing)
        print("语法验证(语法修复后的SQL)：", yufa)

        if  float(yuyimoxing) >= 0.8 and yufa == sql:
            return "正确"+sql  # 如果所有条件都满足，返回 sql 并结束循环
        else:
            Candidate_result=generate_sql_model22(Professional_vocabulary, user_question, user_question_type, class_names, similar_records,model_name)
            sql_query=generate_sql_model33(client,Candidate_result, user_question,model_name)
        sql = sql_query
    return "错误"+sql
def all3(model,client,user_question,model_name,tisi,Professional_vocabulary,similar_records,debug_count,class_names,user_question_type):
    print("生成-候选生成与候选选择-语义验证-语法验证-修复-对齐输出")
    print("-----------------------------------------")
    for _ in range(int(debug_count)):  # 根据 debug_count 控制循环次数
        Candidate_result=generate_sql_model22(Professional_vocabulary, user_question, user_question_type, class_names, similar_records,model_name)
        sql=generate_sql_model33(client,Candidate_result, user_question,model_name)
        print("sql:::::",sql)
        yuyimoxing = generate_sql_model88(sql, user_question, model_name)
        yufa = generate_sql_model100(sql, model_name)
        print("语义验证（验证成功>0.8,验证失败<0.8）：", yuyimoxing)
        print("语法验证(语法修复后的SQL)：", yufa)
        if  float(yuyimoxing)  >= 0.8 and yufa == sql:
            return "正确"+sql  # 如果所有条件都满足，返回 sql 并结束循环
    return "错误"+sql


def all4(cursor,model,client,user_question,model_name,tisi,Professional_vocabulary,similar_records,debug_count,class_names,user_question_type):
    print("生成-执行验证-修复-对齐输出")
    print("-----------------------------------------")
    for _ in range(int(debug_count)):  # 根据 debug_count 控制循环次数
        sql = generate_sql_model66(Professional_vocabulary,similar_records,class_names,user_question_type,tisi, user_question, model_name)
        print("sql:::::",sql)
        zhixing = generate_sql_model55(cursor,sql)
        print("执行结果：", zhixing)
        if zhixing == "正确":
            return "正确"+sql  # 如果所有条件都满足，返回 sql 并结束循环
        result = ("执行结果：" + zhixing)
        sql_query = generate_sql_model11(Professional_vocabulary,user_question_type,class_names,similar_records,user_question, sql, model, client, model_name, result)
        sql = sql_query
    return "错误"+sql


def all5(model,client,user_question,model_name,tisi,Professional_vocabulary,similar_records,debug_count,class_names,user_question_type):
    print("生成-值验证-修复-对齐输出")
    print("-----------------------------------------")
    for _ in range(int(debug_count)):  # 根据 debug_count 控制循环次数
        sql = generate_sql_model66(Professional_vocabulary,similar_records,class_names,user_question_type,tisi, user_question, model_name)
        print("sql:::::",sql)
        zhiyanzheng = generate_sql_model44(user_question, sql, model_name)
        print("值验证（验证成功1,验证失败0）：", zhiyanzheng)
        if zhiyanzheng == "1":
            return "正确"+sql  # 如果所有条件都满足，返回 sql 并结束循环
        result = ("值验证（验证成功1,验证失败0）：" + zhiyanzheng)
        sql_query = generate_sql_model11(Professional_vocabulary,user_question_type,class_names,similar_records,user_question, sql, model, client, model_name, result)
        sql = sql_query
    return "错误"+sql

def all6(cursor,model,client,user_question,model_name,tisi,Professional_vocabulary,similar_records,debug_count,class_names,user_question_type):
    print("生成-执行验证-值验证-修复-对齐输出")
    print("-----------------------------------------")
    for _ in range(int(debug_count)):  # 根据 debug_count 控制循环次数
        sql = generate_sql_model66(Professional_vocabulary,similar_records,class_names,user_question_type,tisi, user_question, model_name)
        print("sql:::::",sql)
        zhixing = generate_sql_model55(cursor,sql)
        zhiyanzheng = generate_sql_model44(user_question, sql, model_name)
        print("执行结果：", zhixing)
        print("值验证（验证成功1,验证失败0）：", zhiyanzheng)
        if zhixing == "正确" and zhiyanzheng == "1":
            return "正确"+sql  # 如果所有条件都满足，返回 sql 并结束循环
        result = (
            "执行结果：" + zhixing +
            "。值验证（验证成功1,验证失败0）：" + zhiyanzheng +
            "。"
        )
        sql_query = generate_sql_model11(Professional_vocabulary,user_question_type,class_names,similar_records,user_question, sql, model, client, model_name, result)
        sql = sql_query
    return "错误"+sql


def all7(model,client,user_question,model_name,tisi,Professional_vocabulary,similar_records,debug_count,class_names,user_question_type):
    print("生成-自检查-修复-对齐输出")
    print("-----------------------------------------")
    for _ in range(int(debug_count)):  # 根据 debug_count 控制循环次数
        sql = generate_sql_model66(Professional_vocabulary,similar_records,class_names,user_question_type,tisi, user_question, model_name)
        print("sql:::::",sql)
        zhijiancha = generate_sql_model77(Professional_vocabulary,similar_records,class_names,user_question_type,user_question,sql,model_name)
        print("自检查结果：", zhijiancha)
        if sql==zhijiancha:
            return "正确"+sql  # 如果所有条件都满足，返回 sql 并结束循环
        result = (
            "自检查：" + zhijiancha +"。"
        )
        sql_query = generate_sql_model11(Professional_vocabulary,user_question_type,class_names,similar_records,user_question, sql, model, client, model_name, result)
        sql = sql_query
    return "错误"+sql



def all8(cursor,model,client,user_question,model_name,tisi,Professional_vocabulary,similar_records,debug_count,class_names,user_question_type):
    print("生成-执行验证-自检查-修复-对齐输出")
    print("-----------------------------------------")
    for _ in range(int(debug_count)):  # 根据 debug_count 控制循环次数
        sql = generate_sql_model66(Professional_vocabulary,similar_records,class_names,user_question_type,tisi, user_question, model_name)
        print("sql:::::",sql)
        zhixing = generate_sql_model55(cursor,sql)
        zhijiancha = generate_sql_model77(Professional_vocabulary,similar_records,class_names,user_question_type,user_question,sql,model_name)
        print("执行结果：", zhixing)
        print("自检查结果：", zhijiancha)
        if zhixing=='正确' and sql==zhijiancha:
            return "正确"+sql  # 如果所有条件都满足，返回 sql 并结束循环
        result = (
            "执行结果：" + zhixing +"。"+"自检查结果：" + zhijiancha +"。"
        )
        sql_query = generate_sql_model11(Professional_vocabulary,user_question_type,class_names,similar_records,user_question, sql, model, client, model_name, result)
        sql = sql_query
    return "错误"+sql


def all9(cursor,model,client,user_question,model_name,tisi,Professional_vocabulary,similar_records,debug_count,class_names,user_question_type):
    print("生成-执行验证-自检查-值验证-修复-对齐输出")
    print("-----------------------------------------")
    for _ in range(int(debug_count)):  # 根据 debug_count 控制循环次数
        sql = generate_sql_model66(Professional_vocabulary,similar_records,class_names,user_question_type,tisi, user_question, model_name)
        print("sql:::::",sql)
        zhixing = generate_sql_model55(cursor,sql)
        zhijiancha = generate_sql_model77(Professional_vocabulary,similar_records,class_names,user_question_type,user_question,sql,model_name)
        zhiyanzheng = generate_sql_model44(user_question, sql, model_name)
        print("执行结果：", zhixing)
        print("自检查结果：", zhijiancha)
        print("值验证结果：", zhiyanzheng)
        if zhixing=='正确' and sql==zhijiancha and zhiyanzheng == "1":
            return "正确"+sql  # 如果所有条件都满足，返回 sql 并结束循环
        result = (
            "执行结果：" + zhixing +"。"+"自检查结果：" + zhijiancha +"。"+"值验证结果：" + zhiyanzheng +"。"
        )
        sql_query = generate_sql_model11(Professional_vocabulary,user_question_type,class_names,similar_records,user_question, sql, model, client, model_name, result)
        sql = sql_query
    return "错误"+sql


def all10(model,client,user_question,model_name,tisi,Professional_vocabulary,similar_records,debug_count,class_names,user_question_type):
    print("生成-语义检查-修复-对齐输出")
    print("-----------------------------------------")
    for _ in range(int(debug_count)):  # 根据 debug_count 控制循环次数
        sql = generate_sql_model66(Professional_vocabulary,similar_records,class_names,user_question_type,tisi, user_question, model_name)
        print("sql:::::",sql)
        yuyimoxing = generate_sql_model88(sql, user_question, model_name)
        print("语义验证（验证成功>0.8,验证失败<0.8）：", yuyimoxing)
        if float(yuyimoxing) >= 0.8:
            return "正确"+sql  # 如果所有条件都满足，返回 sql 并结束循环
        result = (
            "语义验证（验证成功>0.8,验证失败<0.8）：", yuyimoxing+"。"
        )
        sql_query = generate_sql_model11(Professional_vocabulary,user_question_type,class_names,similar_records,user_question, sql, model, client, model_name, result)
        sql = sql_query
    return "错误"+sql



def all11(cursor,model,client,user_question,model_name,tisi,Professional_vocabulary,similar_records,debug_count,class_names,user_question_type):
    print("生成-执行验证-语义检查-修复-对齐输出")
    print("-----------------------------------------")
    for _ in range(int(debug_count)):  # 根据 debug_count 控制循环次数
        sql = generate_sql_model66(Professional_vocabulary,similar_records,class_names,user_question_type,tisi, user_question, model_name)
        print("sql:::::",sql)
        zhixing = generate_sql_model55(cursor,sql)
        yuyimoxing = generate_sql_model88(sql, user_question, model_name)
        print("执行结果：", zhixing)
        print("语义验证（验证成功>0.8,验证失败<0.8）：", yuyimoxing)
        if float(yuyimoxing) >= 0.8:
            return "正确"+sql  # 如果所有条件都满足，返回 sql 并结束循环
        result = (
            "执行结果"+zhixing+"。"+"语义验证（验证成功>0.8,验证失败<0.8）：", yuyimoxing+"。"
        )
        sql_query = generate_sql_model11(Professional_vocabulary,user_question_type,class_names,similar_records,user_question, sql, model, client, model_name, result)
        sql = sql_query
    return "错误"+sql


def all12(cursor,model,client,user_question,model_name,tisi,Professional_vocabulary,similar_records,debug_count,class_names,user_question_type):
    print("生成-执行验证-语义检查-值验证-修复-对齐输出")
    print("-----------------------------------------")
    for _ in range(int(debug_count)):  # 根据 debug_count 控制循环次数
        sql = generate_sql_model66(Professional_vocabulary,similar_records,class_names,user_question_type,tisi, user_question, model_name)
        print("sql:::::",sql)
        zhixing = generate_sql_model55(cursor,sql)
        yuyimoxing = generate_sql_model88(sql, user_question, model_name)
        zhiyanzheng = generate_sql_model44(user_question, sql, model_name)
        print("执行结果：", zhixing)
        print("语义验证（验证成功>0.8,验证失败<0.8）：", yuyimoxing)
        print("值验证（验证成功1,验证失败0）：", zhiyanzheng)
        if float(yuyimoxing) >= 0.8:
            return "正确"+sql  # 如果所有条件都满足，返回 sql 并结束循环
        result = (
            "执行结果"+zhixing+"。"+"语义验证（验证成功>0.8,验证失败<0.8）：", yuyimoxing+"。"+"值验证（验证成功1,验证失败0）", zhiyanzheng+"。"
        )
        sql_query = generate_sql_model11(Professional_vocabulary,user_question_type,class_names,similar_records,user_question, sql, model, client, model_name, result)
        sql = sql_query
    return "错误"+sql



def all13(model,client,user_question,model_name,tisi,Professional_vocabulary,similar_records,debug_count,class_names,user_question_type):
    print("生成-语义骨架验证-修复-对齐输出")
    print("-----------------------------------------")
    for _ in range(int(debug_count)):  # 根据 debug_count 控制循环次数
        sql = generate_sql_model66(Professional_vocabulary,similar_records,class_names,user_question_type,tisi, user_question, model_name)
        print("sql:::::",sql)
        yuyigujia = generate_sql_model99(sql, user_question, model_name)
        print("语义骨架验证（验证成功>0.8,验证失败<0.8）：", yuyigujia)
        if float(yuyigujia) >= 0.8:
            return "正确"+sql  # 如果所有条件都满足，返回 sql 并结束循环
        result = (
            "语义骨架验证（验证成功>0.8,验证失败<0.8）：", float(yuyigujia)+"。"
        )
        sql_query = generate_sql_model99(Professional_vocabulary,user_question_type,class_names,similar_records,user_question, sql, model, client, model_name, result)
        sql = sql_query
    return "错误"+sql

def all14(cursor,model,client,user_question,model_name,tisi,Professional_vocabulary,similar_records,debug_count,class_names,user_question_type):
    print("生成-执行验证-语义骨架验证-修复-对齐输出")
    print("-----------------------------------------")
    for _ in range(int(debug_count)):  # 根据 debug_count 控制循环次数
        sql = generate_sql_model66(Professional_vocabulary,similar_records,class_names,user_question_type,tisi, user_question, model_name)
        print("sql:::::",sql)
        yuyigujia = generate_sql_model99(sql, user_question, model_name)
        zhixing = generate_sql_model55(cursor,sql)
        print("执行结果：", zhixing)
        print("语义骨架验证（验证成功>0.8,验证失败<0.8）：", yuyigujia)
        if zhixing=="正确" and float(yuyigujia) >= 0.8:
            return "正确"+sql  # 如果所有条件都满足，返回 sql 并结束循环
        result = (
            "执行结果：", zhixing+"。"+"语义骨架验证（验证成功>0.8,验证失败<0.8）：", yuyigujia+"。"
        )
        sql_query = generate_sql_model99(Professional_vocabulary,user_question_type,class_names,similar_records,user_question, sql, model, client, model_name, result)
        sql = sql_query
    return "错误"+sql


def all15(cursor,model,client,user_question,model_name,tisi,Professional_vocabulary,similar_records,debug_count,class_names,user_question_type):
    print("生成-执行验证-语义骨架验证-值验证-修复-对齐输出")
    print("-----------------------------------------")
    for _ in range(int(debug_count)):  # 根据 debug_count 控制循环次数
        sql = generate_sql_model66(Professional_vocabulary,similar_records,class_names,user_question_type,tisi, user_question, model_name)
        print("sql:::::",sql)
        yuyigujia = generate_sql_model99(sql, user_question, model_name)
        zhixing = generate_sql_model55(cursor,sql)
        zhiyanzheng = generate_sql_model44(user_question, sql, model_name)
        print("执行结果：", zhixing)
        print("语义骨架验证（验证成功>0.8,验证失败<0.8）：", yuyigujia)
        print("值验证（验证成功1,验证失败0）：", zhiyanzheng)
        if zhixing=="正确" and float(yuyigujia) >= 0.8 and zhiyanzheng=="1":
            return "正确"+sql  # 如果所有条件都满足，返回 sql 并结束循环
        result = (
            "执行结果：", zhixing+"。"+"语义骨架验证（验证成功>0.8,验证失败<0.8）：", yuyigujia+"。"+"值验证（验证成功1,验证失败0）：", zhiyanzheng+"。"
        )
        sql_query = generate_sql_model99(Professional_vocabulary,user_question_type,class_names,similar_records,user_question, sql, model, client, model_name, result)
        sql = sql_query
    return "错误"+sql

