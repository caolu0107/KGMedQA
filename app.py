from flask import Flask, request, jsonify
from question_classifier import *
from question_parser import *
from answer_search import *
from flask_cors import CORS, cross_origin
import sqlite3
import json

app = Flask(__name__)
CORS(app, resources=r'/*')

DATABASE = 'users.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE, timeout=10)
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT NOT NULL,
                        password TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS topics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        username TEXT NOT NULL,
                        classifier_context TEXT,
                        parser_context TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        topic_id INTEGER NOT NULL,
                        text TEXT NOT NULL,
                        user BOOLEAN NOT NULL)''')

    conn.commit()
    conn.close()

init_db()

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
        conn.commit()
        return jsonify({'success': True, 'message': '注册成功'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': '用户名已存在'})
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({'success': True, 'message': '登录成功'})
    else:
        return jsonify({'success': False, 'message': '用户名或密码错误'})

@app.route('/api/create_topic', methods=['POST'])
def create_topic():
    data = request.json
    name = data.get('name')
    username = data.get('username')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO topics (name, username) VALUES (?, ?)", (name, username))
    conn.commit()
    topic_id = cursor.lastrowid
    conn.close()

    return jsonify({'topic': {'id': topic_id, 'name': name}})

@app.route('/api/get_topics', methods=['GET'])
def get_topics():
    username = request.args.get('username')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM topics WHERE username = ?", (username,))
    topics = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    conn.close()

    return jsonify({'topics': topics})

@app.route('/api/delete_topic', methods=['POST'])
def delete_topic():
    data = request.json
    topic_id = data.get('topicId')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE topic_id = ?", (topic_id,))
    cursor.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

@app.route('/api/get_messages', methods=['GET'])
def get_messages():
    topic_id = request.args.get('topicId')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT text, user FROM messages WHERE topic_id = ?", (topic_id,))
    messages = [{'text': row[0], 'user': bool(row[1])} for row in cursor.fetchall()]
    conn.close()

    return jsonify({'messages': messages})

@app.route('/api/save_messages', methods=['POST'])
def save_messages():
    data = request.json
    topic_id = data.get('topicId')
    messages = data.get('messages')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE topic_id = ?", (topic_id,))
    for message in messages:
        cursor.execute("INSERT INTO messages (topic_id, text, user) VALUES (?, ?, ?)",
                       (topic_id, message['text'], int(message['user'])))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

def save_context(topic_id, classifier_context, parser_context):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE topics SET classifier_context = ?, parser_context = ? WHERE id = ?",
                   (json.dumps(classifier_context), json.dumps(parser_context), topic_id))
    conn.commit()
    conn.close()

def load_context(topic_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT classifier_context, parser_context FROM topics WHERE id = ?", (topic_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        classifier_context = json.loads(row[0]) if row[0] else {}
        parser_context = json.loads(row[1]) if row[1] else {}
        return {'classifier_context': classifier_context, 'parser_context': parser_context}
    return {}

classifier = QuestionClassifier()
parser = QuestionPaser()
searcher = AnswerSearcher()

@app.route('/api/send_message', methods=['POST'])
def send_message():
    answer = '您好，我是医药智能助理，希望可以帮到您。祝您身体健康！'
    data = request.get_json()
    user_message = data.get('message')
    topic_id = data.get('topicId')
    print(f"User message: {user_message}")

    # 加载上下文
    context = load_context(topic_id)
    classifier.set_context(context.get('classifier_context', {}))
    parser.set_context(context.get('parser_context', {}))

    res_classify = classifier.classify(user_message)
    # print(f"res_classify: {res_classify}")
    if not res_classify:
        save_message(topic_id, user_message, True)
        save_message(topic_id, answer, False)
        return jsonify({'response': answer})
    res_sql = parser.parser_main(res_classify)
    # print(f"res_sql: {res_sql}")
    final_answers = searcher.search_main(res_sql)
    if not final_answers:
        save_message(topic_id, user_message, True)
        save_message(topic_id, answer, False)
        return jsonify({'response': answer})
    else:
        response = '\n'.join(final_answers)
        save_message(topic_id, user_message, True)
        save_message(topic_id, response, False)
        # 保存上下文
        save_context(topic_id, classifier.get_context(), parser.get_context())
        print(f"Response: {response}")
        return jsonify({'response': response})

def save_message(topic_id, text, user):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (topic_id, text, user) VALUES (?, ?, ?)",
                   (topic_id, text, int(user)))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # app.run(debug=True)
    app.run()
