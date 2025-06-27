import pymysql


def get_db_model(id):
    connection = pymysql.connect(
        host='localhost', user='root', password='123456', database='sys', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
    )
    cursor = connection.cursor()
    cursor.execute('SELECT self_method FROM user WHERE id = %s', (id))
    self_method = cursor.fetchone()
    # 提取字符串内容
    print(self_method)

    # 提取字符串内容
    content = self_method['self_method']

    # 分割字符串
    parts = content.split('；')  # 使用分号分割

    # 初始化结果
    models = []
    debug_count = None

    # 遍历分割后的部分
    for part in parts:
        if '模型选择' in part:
            # 提取模型和方法
            model_parts = part.split('--')
            for model_part in model_parts[1:]:  # 跳过“模型选择”部分
                # 检查 split 结果是否包含两个部分
                split_result = model_part.split('--')
                if len(split_result) == 2:
                    model, method = split_result
                    models.append((model.strip(), method.strip()))
                else:
                    print(f"警告：无法解析的部分：{model_part}")
        elif '自调试次数' in part:
            # 提取自调试次数
            debug_count = part.split(':')[1].replace('次。', '').strip()

    # 输出结果
    print("模型和方法：", models)
    print("自调试次数：", debug_count)
    return models,debug_count

print(get_db_model(2))



