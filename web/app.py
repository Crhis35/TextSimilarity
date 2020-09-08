from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import spacy


app = Flask(__name__)
api = Api(app)

client = MongoClient('mongodb://db:27017')
db = client.SimilarityDB
users = db['Users']


def UserExist(username):
    if users.find({
        "Username": username
    }).count() == 0:
        return False
    else:
        return True


class Register(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData['username']
        password = postedData['password']

        if UserExist(username):
            return jsonify({
                'status': 301,
                'msg': 'Invalid Username'
            })

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert_one({
            'Username': username,
            'Password': hashed_pw,
            'Tokens': 6
        })
        return jsonify({
            'status': 200,
            'msg': 'Succesfully Signed'
        })


def verifyPw(username, password):
    if not UserExist(username):
        return False
    hash_pw = users.find_one({
        'Username': username
    })['Password']

    if bcrypt.hashpw(password.encode('utf8'), hash_pw) == hash_pw:
        return True
    else:
        return False


def countTokens(username):
    return users.find_one({
        'Username': username
    })['Tokens']


class Detect(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData['username']
        password = postedData['password']
        text1 = postedData['text1']
        text2 = postedData['text2']

        if not UserExist(username):
            return jsonify({
                'status': 301,
                'msg': 'Invalid Username'
            })
        correct_pw = verifyPw(username, password)

        if not correct_pw:
            return jsonify({
                'status': 302,
                'msg': 'Invalid Password'
            })
        num_tokens = countTokens(username)
        if num_tokens < 1:
            return jsonify({
                'status': 303,
                'msg': 'You are out of tokens, please refill'
            })
        nlp = spacy.load('en_core_web_sm')

        text1 = nlp(text1)
        text2 = nlp(text2)

        # Ratio is a number between 0 and 1 the closer to 1 the more similar

        ratio = text1.similarity(text2)
        users.update_one({
            'Username': username,
        }, {
            '$set': {
                'Tokens': num_tokens-1
            }
        })
        return jsonify({
            'status': 200,
            'similarity': ratio,
            'msg': 'Similarity score calculated successfully'
        })


class Refill(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData['username']
        password = postedData['password']
        refill_amount = postedData['refill']

        if not UserExist(username):
            return jsonify({
                'status': 301,
                'msg': 'Invalid Username'
            })

        correct_pw = "abc123"

        if not password == correct_pw:
            return jsonify({
                'status': 304,
                'msg': 'Invalid Admin Password'
            })

        users.update({
            'Username': username
        }, {
            '$set': refill_amount
        })

        return jsonify({
            'status': 200,
            'msg': 'Refilled successfully'
        })


api.add_resource(Register, '/register')
api.add_resource(Detect, '/detect')
api.add_resource(Refill, '/refill')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
