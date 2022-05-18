from datetime import datetime, timedelta
import hashlib
import json
from bson import ObjectId
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import jwt
from pymongo import MongoClient
# from bson.json_util import loads, dumps

SECRET_KEY = 'turtle'


app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
client = MongoClient('localhost', 27017)
db = client.turtlegram


@app.route("/")
def hello_world():
    return jsonify({'message': 'success'})


@app.route("/signup", methods=["POST"])
def sign_up():
    data = json.loads(request.data)
    # data = loads(request.data)
    print(data.get('email'))
    print(data["password"])

    # 이메일 중복시 에러처리

    # 비밀번호 해싱
    pw = data.get('password', None)
    hashed_password = hashlib.sha256(pw.encode('utf-8')).hexdigest()

    doc = {
        'email': data.get('email'),
        'password': hashed_password
    }

    # doc = {
    #     'email': data.get('email'),
    #     'password': data.get('password')
    # }

    print(doc)
    user = db.users.insert_one(doc)
    print(doc)

    return jsonify({"status": "success"})

    # # dump 사용
    # json_doc = dumps(doc)
    # print(json_doc)
    # return json_doc


@app.route("/login", methods=["POST"])
def login():
    print(request)
    data = json.loads(request.data)
    print(data)

    email = data.get("email")
    password = data.get("password")
    hashed_pw = hashlib.sha256(password.encode('utf-8')).hexdigest()
    print(hashed_pw)

    result = db.users.find_one({
        'email': email,
        'password': hashed_pw
    })
    print(result)

    if result is None:
        return jsonify({"message": "아이디나 비밀번호가 옳지 않습니다."}), 401

    payload = {
        'id': str(result["_id"]),
        'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    print(token)

    return jsonify({"message": "success", "token": token})


@app.route("/getuserinfo", methods=["GET"])
def get_user_info():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"message": "no token"}), 402

    user = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    result = db.users.find_one({
        '_id': ObjectId(user["id"])
    })

    return jsonify({"message": "success", "email": result["email"]})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5002, debug=True)
