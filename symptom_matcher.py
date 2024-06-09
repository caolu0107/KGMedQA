'''symptom_matcher.py: 症状匹配模块'''

from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import torch


class SymptomMatcher:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained('./simbert-chinese-base')
        self.model = BertModel.from_pretrained('./simbert-chinese-base')
        # print("模型和分词器已加载")

        with open('dict/symptom.txt', 'r', encoding='utf-8') as file:
            self.symptoms = file.read().splitlines()

        self.embedding_file = 'symptom_embeddings.npy'
        self.embedding_dim = 768
        self.num_symptoms = len(self.symptoms)

        # 读取内存映射文件
        self.symptom_embeddings = np.memmap('symptom_embeddings.npy', dtype='float32', mode='r',
                                            shape=(self.num_symptoms, self.embedding_dim))
        # print("症状嵌入已加载")
        print("simBert model init finished ......")

    def get_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors='pt')
        outputs = self.model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1)
        return embedding

    def find_best_match(self, user_input):
        # 获取用户输入的嵌入并转换为 NumPy 数组
        user_embedding = self.get_embedding(user_input).detach().cpu().numpy()
        # 计算相似度
        similarities = cosine_similarity(user_embedding.reshape(1, -1), self.symptom_embeddings)
        # 获取最匹配的症状索引
        best_match_index = similarities.argmax()
        # print(f"用户输入: {user_input}，匹配到的症状: {self.symptoms[best_match_index]}")
        return self.symptoms[best_match_index]


if __name__ == '__main__':
    matcher = SymptomMatcher()
    # 测试用户输入
    user_input = "怎么治疗"
    matched_symptom = matcher.find_best_match(user_input)
    print(f"用户输入: {user_input}，匹配到的症状: {matched_symptom}")
