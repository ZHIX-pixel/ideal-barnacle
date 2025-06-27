import pymysql
import weaviate
from sentence_transformers import SentenceTransformer
from text2vec import SentenceModel

# 初始化 Weaviate 客户端
client = weaviate.Client("http://localhost:8080")  # 假设 Weaviate 运行在 localhost 上

# 初始化 Text2Vec 模型
text2vec_model = SentenceTransformer('D:/my_langchain/myProject1/text2vec-base-chinese')

# 连接到 MySQL 数据库
connection = pymysql.connect(
    host='localhost', user='root', password='123456', database='lhr', charset='utf8mb4'
)


def vectorize_text(text):
    """使用 Text2Vec 将文本转换为向量"""
    return text2vec_model.encode([text])[0]


def delete_weaviate_class(class_name):
    """删除已存在的 Weaviate 类"""
    try:
        client.schema.delete_class(class_name)
        print(f"Class {class_name} deleted successfully.")
    except Exception as e:
        print(f"Error deleting class {class_name}: {e}")


def map_mysql_type_to_weaviate_type(mysql_type):
    """根据 MySQL 类型映射到 Weaviate 支持的类型"""
    if not mysql_type:
        # 如果 mysql_type 为 None 或空字符串，使用默认值 'text'
        return "text"

    mysql_type = mysql_type.lower()  # 转小写以避免大小写问题
    print("mysql_type",mysql_type)
    if mysql_type.startswith("int") or mysql_type.startswith("bigint"):
        return "number"
    elif mysql_type.startswith("decimal") or mysql_type.startswith("float") or mysql_type.startswith("double"):
        return "number"
    elif mysql_type.startswith("date") or mysql_type.startswith("time"):
        return "date"
    elif mysql_type.startswith("varchar") or mysql_type.startswith("text"):
        return "text"
    elif mysql_type.startswith("blob"):
        return "blob"
    else:
        return "text"  # 默认使用 text 类型


def create_weaviate_class(table_name, columns, column_types, table_description, primary_keys, foreign_keys):
    """根据表和列信息在 Weaviate 中创建类"""
    class_name = table_name.replace(" ", "_")  # Weaviate 类名不能包含空格，替换为下划线

    # 删除已存在的类
    delete_weaviate_class(class_name)

    # 创建基础的 Weaviate 类结构
    class_obj = {
        "class": class_name + ("_" + table_description.replace(" ", "_") if table_description else ""),  # 类名加上表描述
        "properties": [],
        "vectorIndexConfig": {"distance": "l2-squared"}
    }

    # 为表添加一个“key_type”列，表示字段的类型（主键、外键、普通）作为辅助信息
    key_type_column = {
        "name": "other_information",
        "dataType": ["text"]  # 假设 key_type 字段是文本类型
    }
    class_obj["properties"].append(key_type_column)

    # 处理每一列，检查它是主键、外键还是普通字段
    for column in columns:
        # 获取列的数据类型
        mysql_type = column_types.get(column, {}).get('type', "text")  # 获取列的数据类型（如果没有则默认为 "text"）
        weaviate_type = map_mysql_type_to_weaviate_type(mysql_type)  # 映射到 Weaviate 类型

        # 如果是 "id"，重命名为 "vector_idd"
        if column == "id":
            column = "vector_idd"  # 将 id 重命名为 vector_idd

        column_info = {
            "name": column,
            "dataType": [weaviate_type]  # 使用映射后的 Weaviate 类型
        }

        # 将列信息添加到类结构中
        class_obj["properties"].append(column_info)

    print("class_obj:::::", class_obj)

    # 向 Weaviate 创建类
    try:
        client.schema.create_class(class_obj)
        print(f"Class {class_name} created successfully.")
    except Exception as e:
        print(f"Error creating class {class_name}: {e}")


def insert_data_into_weaviate(table_name, rows, column_names, primary_keys, foreign_keys):
    """将表数据插入 Weaviate，并标记主键和外键"""
    # 用一个集合来记录已经处理过的主外键信息，避免重复存储
    processed_info = set()

    for row in rows:
        data = {}

        # 动态地为每个字段创建键值对
        for column in column_names:
            # 如果是 "id"，将其重命名为 "vector_idd"
            if column == "id":
                column_name = "vector_idd"
            else:
                column_name = column
            data[column_name] = row[column]

        # 初始化 each_row_related_info 用于存储当前行的主外键信息
        each_row_related_info = []

        # 遍历主键，检查是否存在于当前行
        for pk in primary_keys:
            if pk in row:  # 如果该主键在当前行中存在
                key_info = f"{pk} is a primary key"
                if key_info not in processed_info:  # 如果该信息未处理过
                    each_row_related_info.append(key_info)
                    processed_info.add(key_info)  # 记录该信息

        # 遍历外键，检查是否存在于当前行
        for fk in foreign_keys:
            if fk['column_name'] in row:  # 如果该外键在当前行中存在
                key_info = f"{fk['column_name']} is a foreign key to {fk['foreign_table']}({fk['foreign_column']})"
                if key_info not in processed_info:  # 如果该信息未处理过
                    each_row_related_info.append(key_info)
                    processed_info.add(key_info)  # 记录该信息

        # 为当前行设置 unique 的 other_information
        data['other_information'] = ", ".join(each_row_related_info) if each_row_related_info else None

        # 向 Weaviate 插入数据
        try:
            client.data_object.create(data, table_name)
            print(f"Data inserted into class {table_name}")
        except Exception as e:
            print(f"Error inserting data into class {table_name}: {e}")


def get_table_data(cursor, table_name):
    """从 MySQL 获取表的数据"""
    cursor.execute(f"SELECT * FROM {table_name}")  # 限制为查询前 10 条数据
    columns = cursor.description
    rows = cursor.fetchall()

    # 获取列名并组织成字典
    column_names = [column[0] for column in columns]
    data_rows = []
    for row in rows:
        data_row = {}
        for i, column in enumerate(column_names):
            data_row[column] = row[i]
        data_rows.append(data_row)

    return data_rows, column_names


def get_table_description(cursor, table_name):
    """获取表的描述"""
    cursor.execute(f"SHOW TABLE STATUS LIKE '{table_name}'")
    table_description = cursor.fetchone()
    if table_description and table_description[17]:
        return table_description[17]
    return None


def get_column_descriptions(cursor, table_name):
    """获取表内列的描述"""
    cursor.execute(f"SHOW FULL COLUMNS FROM {table_name}")
    columns = cursor.fetchall()
    column_info = {}
    for column in columns:
        column_name = column[0]
        column_type = column[1]  # 数据类型通常在第二位
        column_comment = column[8] if column[8] else None  # 描述通常在第8位
        column_info[column_name] = {
            "type": column_type,
            "comment": column_comment
        }
    return column_info


def get_primary_keys(cursor, table_name):
    """获取表的主键"""
    cursor.execute(f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'")
    primary_keys = cursor.fetchall()
    return [key[4] for key in primary_keys]  # 主键列名在第 4 位


def get_foreign_keys(cursor, table_name):
    """获取表的外键"""
    cursor.execute(f"""
        SELECT kcu.column_name, 
               kcu.referenced_table_name AS foreign_table_name, 
               kcu.referenced_column_name AS foreign_column_name
        FROM information_schema.key_column_usage kcu
        WHERE kcu.table_name = '{table_name}' 
            AND kcu.table_schema = DATABASE()
            AND kcu.referenced_table_name IS NOT NULL
    """)
    foreign_keys = cursor.fetchall()
    fk_info = []
    for fk in foreign_keys:
        fk_info.append({
            'column_name': fk[0],
            'foreign_table': fk[1],
            'foreign_column': fk[2]
        })
    return fk_info


def main1(cursor):
    # 获取所有表
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        print(f"Processing table: {table_name}")

        # 获取表的其他信息
        table_description = get_table_description(cursor, table_name)
        columns_info = get_column_descriptions(cursor, table_name)
        primary_keys = get_primary_keys(cursor, table_name)
        foreign_keys = get_foreign_keys(cursor, table_name)

        # 获取表数据
        rows, column_names = get_table_data(cursor, table_name)

        # 在 Weaviate 创建表类
        create_weaviate_class(table_name, column_names, columns_info, table_description, primary_keys, foreign_keys)

        # 将数据插入 Weaviate
        insert_data_into_weaviate(table_name, rows, column_names, primary_keys, foreign_keys)

    cursor.close()
    connection.close()


if __name__ == "__main__":
    db_config = {
        "host": "localhost",  # 数据库主机
        "user": "root",  # 数据库用户名
        "password": "123456",  # 数据库密码
        "database": "sys1"  # 数据库名称
    }
    # 创建数据库连接
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    main1(cursor)
