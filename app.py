'''app.py: 问答系统接口'''

from flask import Flask, request, jsonify
import json
from question_classifier import *
from question_parser import *
from answer_search import *
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, resources=r'/*')


classifier = QuestionClassifier()
parser = QuestionPaser()
searcher = AnswerSearcher()

@app.route('/send_message', methods=['POST'])
def send_message():
    answer = '您好，我是医药智能助理，希望可以帮到您。祝您身体健康！'
    data = request.get_json()
    user_message = data.get('message')
    print(f"User message: {user_message}")

    res_classify = classifier.classify(user_message)
    if not res_classify:
        return jsonify({'response': answer})
    res_sql = parser.parser_main(res_classify)
    final_answers = searcher.search_main(res_sql)
    if not final_answers:
        return jsonify({'response': answer})
    else:
        return jsonify({'response': '\n'.join(final_answers)})


if __name__ == '__main__':
    app.run(debug=True)

