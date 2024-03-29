from flask import Flask, request, jsonify, make_response
from firebase_admin import credentials, firestore, initialize_app, db
import os
from googletrans import Translator
import requests


#initialize Flask
app = Flask(__name__)

#initialize Firestore DB
cred = credentials.Certificate('firebase.json')
default_app = initialize_app(cred)
db = firestore.client()

#initialize Google Translate
translator = Translator()

#creates collection
users_ref = db.collection('users')

@app.route('/translate', methods = ['POST'])
def translate():
    try:
        d = {}
        word_json = request.json
        word = word_json["word"]
        word_1 = ''.join(word.split())
        language = word_json["language"]
        translated_word = translator.translate(word, dest = language)
        d["translated_word"] = translated_word.text
        d["translated_pron"] = translated_word.pronunciation
        url = ("https://wordsapiv1.p.rapidapi.com/words/{}/definition".format(word))
        response = requests.request("GET", url, headers=headers)
        d["definition"] = response.json()["definition"]
        users_ref.document("translated_words").update({word_1 : d})
        return make_response(jsonify(d), 200)
    except Exception as error:
        return "Error: {}".format(error)

@app.route('/getall', methods = ['GET'])
def getall():
    try:
        doc_ref = db.collection('users').document("translated_words")
        doc = doc_ref.get().to_dict()
        return make_response(jsonify(doc), 200)
    except Exception as error:
        return "Error: {}".format(error)

@app.route('/deleteall', methods = ["DELETE"])
def deleteall():
    try:
        users_ref.document("translated_words").set({})
        return jsonify({"success": True}, 200)
    except Exception as error:
        return "Error: {}".format(error)


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
