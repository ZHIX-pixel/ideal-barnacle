import re
from zhipuai import ZhipuAI


class KeywordSimilarityExtractor:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = ZhipuAI(api_key=self.api_key)

    def get_response(self, question):
        """根据用户问题从ZhipuAI获取相似词和翻译的响应"""
        prompt_t = f"""
            我要根据用户问题的关键词相似性检索数据库来选择与用户问题最相关的数据表。
            提取的关键词不能是太简单的，太通用的。因为我用关键词是未来定位最相关的表。
            从以下用户问题中提取相关的关键词，并为每个关键词提供其英文翻译同时生成两个相似词及相似词英文翻译。
            用户问题: {question}
            例如:用户问题:user_question = "获取“material_appropriation”表中所有类型为“领用”的记录。"
            输出:# 提取关键词
            keywords = ["material_appropriation","领用"]
            # 定义关键词的英文翻译
            keywords_translation = ["material_appropriation", "type", "appropriation"]
            # 定义关键词的相似词及相似词的英文翻译
            similar_words = [
                ["material_appropriation", "物资领用", "资源调配"],
                ["领用", "借用", "使用"]
            ]
            similar_words_translation = [
                ["material_appropriation", "Material Appropriation", "Resource Allocation"],
                ["appropriation", "borrow", "use"]
            ]
        """
        completion = self.client.chat.completions.create(
            model="glm-4-air",
            messages=[{"role": "system", "content": ""},
                      {"role": "user", "content": prompt_t}],
            temperature=0.1,
        )
        response = completion.choices[0].message.content
        return response

    def extract_variable(self, text, var_name):
        """从响应文本中提取指定变量的值（如相似词）"""
        start_index = text.find(var_name)
        if start_index == -1:
            return None

        start_index = text.find('[', start_index)
        balance = 0
        for i in range(start_index, len(text)):
            if text[i] == '[':
                balance += 1
            elif text[i] == ']':
                balance -= 1
            if balance == 0:
                end_index = i + 1
                break
        return text[start_index:end_index]

    def extract_double_quoted_content(self, text):
        """提取字符串中所有双引号之间的内容"""
        if text is None:
            return []
        return re.findall(r'"(.*?)"', text)

    def get_similar_words_and_translation(self, question):
        """获取并提取关键词的相似词和相似词的英文翻译"""
        # 获取响应文本
        zhipu_AI_out = self.get_response(question)

        # 提取相似词和翻译的原始字符串
        similar_words_str = self.extract_variable(zhipu_AI_out, 'similar_words')
        similar_words_translation_str = self.extract_variable(zhipu_AI_out, 'similar_words_translation')

        # 检查提取的字符串是否有效
        if similar_words_str is None or similar_words_translation_str is None:
            print("Error: Missing expected variables in the response.")
            return []

        # 提取双引号中的内容
        all_pairs = (
                self.extract_double_quoted_content(similar_words_str) +
                self.extract_double_quoted_content(similar_words_translation_str)
        )

        return all_pairs


# 示例调用
if __name__ == "__main__":
    # 初始化ZhipuAI API
    api_key = "f7a0186af1f5730d592e6bb15b7e9961.3i3qcCyOf2VeWUVs"
    extractor = KeywordSimilarityExtractor(api_key)

    # 用户问题
    question = "获取“material_appropriation”表中所有类型为“领用”的记录。"

    # 获取相似词及其翻译
    result = extractor.get_similar_words_and_translation(question)

    # 输出结果
    print("提取的相似词及翻译:", result)
