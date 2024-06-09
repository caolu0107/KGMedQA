
# 基于知识图谱的智能医药问答系统

## 目录

- [项目简介](#项目简介)
- [安装与运行](#安装与运行)
- [API 端点](#api-端点)
- [项目结构](#项目结构)
- [数据库初始化](#数据库初始化)
- [依赖项](#依赖项)
- [知识图谱构建](#知识图谱构建)
- [问句分类与解析](#问句分类与解析)
- [贡献指南](#贡献指南)
- [许可协议](#许可协议)

## 项目简介

“基于知识图谱的智能医药问答系统”是一个基于 Flask 构建的 Web 服务，结合了自然语言处理技术和知识图谱，为用户提供医疗问题的智能回答。用户可以通过发送消息获取关于疾病、症状、治疗方法等方面的建议和信息。

## 安装与运行

1. **克隆项目**

    ```bash
    git clone https://github.com/caolu0107/KGMedQA
    cd KGMedQA
    ```
    下载并保存SimBERT模型到本地
        访问 Hugging Face 上的 SimBERT 模型页面(https://huggingface.co/peterchou/simbert-chinese-base)。
        下载模型文件并将其保存到本地目录，例如 ./simbert-chinese-base。

2. **创建虚拟环境并安装依赖项**

    ```bash
    python3.8 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3. **知识图谱构建**

    `build_medicalgraph.py` 脚本用于将 `medical.json` 中的医疗数据导入 Neo4j 知识图谱。
   需下载neo4j桌面版，创建一个新的数据库，然后在`build_medicalgraph.py`中修改数据库连接信息。
   neo4j数据库版本选择4.2.19(测试可运行)。

    ```bash
    python build_medicalgraph.py
    ```

4. **运行应用**

    ```bash
    python app.py
    ```

    应用将运行在 `http://127.0.0.1:5000/`。

## API 端点

- `POST /api/register` - 注册新用户
- `POST /api/login` - 用户登录
- `POST /api/create_topic` - 创建新话题
- `GET /api/get_topics` - 获取用户话题
- `POST /api/delete_topic` - 删除话题
- `GET /api/get_messages` - 获取话题中的消息
- `POST /api/save_messages` - 保存话题中的消息
- `POST /api/send_message` - 发送消息并获取回答

## 项目结构

```plaintext
KGMedQA/
├── data/
|    └── medical.json     # 医疗数据
├── dict/                 # 医疗数据词典
├── prepare_data/
|    ├── build_data.py    #数据预处理
|    ├── data_spider.py   #数据爬取
|    └── max_cut.py       最大匹配分词算法
├── simbert-chinese-base/# simBERT 模型
├── answer_search.py     # 答案搜索模块
├── app.py               # Flask 应用主文件
├── build_medicalgraph.py# 知识图谱数据导入脚本
├── build_symptonmatcher.py# 构建症状嵌入文件
├── chatbot_graph.py     # 问答系统后端测试程序
├── question_classifier.py  # 问句分类器
├── question_parser.py   # 问题解析模块
├── requirements.txt     # 项目依赖项
├── spacy_matcher.py     # spaCy 主语匹配模块
├── symptom_embeddings.npy#症状嵌入文件
├── symptom_matcher.py   # 症状匹配模块
└── users.db             # 用户数据库
```

## 数据库初始化

`app.py` 中包含数据库初始化逻辑，首次运行应用时将自动创建数据库和所需表：

- `users` - 存储用户信息
- `topics` - 存储话题信息
- `messages` - 存储消息内容

## 依赖项

- Flask
- Flask-CORS
- sqlite3
- py2neo
- transformers (BERT)
- spacy
- torch

安装依赖项：

```bash
pip install -r requirements.txt
```



## 问句分类与解析

- `question_classifier.py` - 问句分类器，用于识别问句中的实体和意图。
- `question_parser.py` - 问题解析模块，将问句转换为相应的数据库查询语句。
- `answer_search.py` - 执行查询并返回格式化的答案。

## 贡献指南

欢迎对本项目提出建议和贡献代码。请先 Fork 本项目并创建新分支进行修改，测试后提交 Pull Request。

## 许可协议

本项目使用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

感谢您使用“基于知识图谱的智能医药问答系统”！希望它能为您提供帮助。
