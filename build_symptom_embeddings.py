'''build_symptom_embeddings.py: 构建症状嵌入文件（symptom_embeddings.npy）'''

import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import pickle

# 使用 SimBERT 模型
tokenizer = BertTokenizer.from_pretrained('./simbert-chinese-base')
model = BertModel.from_pretrained('./simbert-chinese-base')
print("模型和分词器已加载")

def get_embedding(text):
    inputs = tokenizer(text, return_tensors='pt')
    outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1)
    print(text)
    return embedding

# 加载症状列表
with open('dict/symptom.txt', 'r', encoding='utf-8') as file:
    symptoms = file.read().splitlines()

embedding_file = 'symptom_embeddings.npy'
batch_size = 100  # 每次处理的条数
embedding_dim = 768  # 嵌入维度
num_symptoms = len(symptoms)

# 创建一个内存映射文件
if not os.path.exists(embedding_file):
    symptom_embeddings = np.memmap(embedding_file, dtype='float32', mode='w+', shape=(num_symptoms, embedding_dim))
else:
    symptom_embeddings = np.memmap(embedding_file, dtype='float32', mode='r+', shape=(num_symptoms, embedding_dim))

# 分批处理
for i in range(0, num_symptoms, batch_size):
    batch_symptoms = symptoms[i:i + batch_size]
    batch_embeddings = [get_embedding(symptom).detach().numpy() for symptom in batch_symptoms]
    symptom_embeddings[i:i + batch_size] = np.vstack(batch_embeddings)
    print(f"处理并保存了{i + batch_size}个症状嵌入")
    # 释放内存
    del batch_embeddings
    torch.cuda.empty_cache()

# 确保所有数据都写入磁盘
symptom_embeddings.flush()
print("所有症状嵌入已生成并保存")

def find_best_match(user_input):
    user_embedding = get_embedding(user_input).detach().numpy()
    symptom_embeddings = np.memmap(embedding_file, dtype='float32', mode='r', shape=(num_symptoms, embedding_dim))
    similarities = cosine_similarity(user_embedding.reshape(1, -1), symptom_embeddings)
    best_match_index = similarities.argmax()
    return symptoms[best_match_index]

# 测试用户输入
user_input = "头疼"
matched_symptom = find_best_match(user_input)
print(f"用户输入: {user_input}，匹配到的症状: {matched_symptom}")
