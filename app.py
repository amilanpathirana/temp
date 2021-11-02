from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL


import os
import json
from utils import update_logger, predict_json

import numpy as np

import pickle
import pandas as pd

from sklearn.preprocessing import LabelEncoder
import joblib

local = 1


clf = joblib.load('filename.pkl')

app = Flask(__name__)
mysql = MySQL(app)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'amila123'
app.config['MYSQL_DB'] = 'submissions_db'


MAKES = [
    'honda',
    'ford',
    'toyota',
    'nissan',
    'mazda'
]

YEARS = list(range(2000, 2022))


@app.route("/", methods=["GET", 'POST'])
def index():
    return render_template('index.html', makes=MAKES, years=YEARS)


@app.route("/calculate", methods=['POST'])
def calculate():
    make = request.form.get('make')
    year = request.form.get('year')
    name = request.form.get('name')
    email = request.form.get('email')

    km2 = 1
    km1 = 10
    hp = 1000

    infdf = pd.DataFrame({'make': [make], 'year': [year], 'highwaympg': [
                         km2], 'citympg': [km1], 'enginehp': [hp]})
    pkl_file = open('label_encoder.pkl', 'rb')
    le_departure = pickle.load(pkl_file)
    pkl_file.close()
    infdf['make'] = le_departure.transform(infdf['make'])

    image1 = np.array(infdf)

    preds = clf.predict(image1)
    print("Running local model")

    prediction = round(preds[0])

    print(prediction)

    if not name:
        return render_template('index.html', message="Enter Your Name", makes=MAKES, years=YEARS)
    if not email:
        return render_template('index.html', message="Enter Your Email", makes=MAKES, years=YEARS)
    if not make:
        return render_template('index.html', message="Select Make", makes=MAKES, years=YEARS)
    if not year:
        return render_template('index.html', message="Select Year", makes=MAKES, years=YEARS)

    if make not in MAKES:

        return render_template('index.html', message="Invalid Input",  makes=MAKES, years=YEARS)

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO submissions (name, make) VALUES(%s,%s)", (name, make))
    mysql.connection.commit()
    cur.close()
    return render_template('results.html', prediction=prediction)
