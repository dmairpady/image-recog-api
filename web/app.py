from  flask import Flask,jsonify,request
from flask_restful import Api,Resource
from pymongo import MongoClient
import bcrypt
import numpy
import requests
import subprocess
import json

app=Flask(__name__)
api=Api(app)

client=MongoClient("mongodb://db:27017")

db=client.imageRecognition

users=db["Users"]


def formjson(statuscode,message):
    retJson={
        'Status':statuscode,
        'Message':message
    }
    return retJson


def userexist(username):
    if users. count_documents({'username':username})==0:
        return False
    else:
        return True


def verifypw(username,password):
    hashed_pw=users.find({
        "username":username
    })[0]['password']

    if bcrypt.hashpw(password.encode('utf8'),hashed_pw) == hashed_pw:
        return True
    else:
        return False


class Register(Resource):
    def post(self):
        postedData=request.get_json()
        username=postedData['username']
        password=postedData['password']
        if userexist(username):
            retjson=formjson(301,'Username already exist')
            return jsonify(retjson)

        hashed_pw=bcrypt.hashpw(password.encode('utf8'),bcrypt.gensalt())

        users.insert_one({
            "username":username,
            "password":hashed_pw,
            "tokens":4
        })

        retJson=formjson(200,"You have successfully  signed up for API")
        return jsonify(retJson)


class Classify(Resource):
    def post(self):
        postedData=request.get_json()
        username=postedData['username']
        password=postedData['password']
        url=postedData['url']
        if not userexist(username):
            retjson = formjson(301,'Username doesnt exist')
            return jsonify(retjson)

        if not verifypw(username,password):
            retjson=formjson(302,'Password doesnt match')
            return jsonify(retjson)

        current_tokens=users.find({
            "username":username
        })[0]["tokens"]

        if current_tokens<=0:
            retjson=formjson(303,'Token expired')
            return jsonify(retjson)

        r=requests.get(url)
        retjson={}
        with open("temp.jpg","wb") as f:
            f.write(r.content)
            proc=subprocess.Popen('python classify_image.py --model_dir=. --image_file=./temp.jpg',shell=True)
            proc.communicate()[0]
            proc.wait()
            with open("text.txt") as g:
                if len(g.readlines()) != 0:
                    g.seek(0)
                    retjson = json.load(g)

        users.update_one({
            'username':username
        },{
            "$set":{
                "tokens": current_tokens-1
            }
        })
        return retjson

class Refill(Resource):
    def post(self):
        postedData=request.get_json()
        username=postedData['username']
        admin_pw=postedData['admin_pw']
        amount=postedData['amount']
        if not userexist(username):
            retjson = formjson(301, 'Username doesnt exist')
            return jsonify(retjson)

        correct_pw="123456"

        if correct_pw !=admin_pw:
            retjson=formjson(303,"Incorrect admin password")
            return jsonify(retjson)

        users.update({
            "username":username
        },{
            "$set":{
                "tokens":amount
            }

        })
        retjson=formjson(200,"Recharged successfully")
        return jsonify(retjson)


api.add_resource(Register,'/register')
api.add_resource(Classify,"/classify")
api.add_resource(Refill,'/refill')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)




