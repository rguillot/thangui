#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import date
import rethinkdb as rdb
from rethinkdb.errors import RqlRuntimeError, RqlDriverError
from time import localtime, strftime
from flask import Flask, request, redirect, flash, render_template, g, jsonify, abort


RDB_HOST =  os.environ.get('RDB_HOST') or 'localhost'
RDB_PORT = os.environ.get('RDB_PORT') or 28015
DB = 'thangui'

def dbSetup():
    connection = rdb.connect(host=RDB_HOST, port=RDB_PORT)
    try:
        rdb.db_create(DB).run(connection)
        rdb.db(DB).table_create('jeux').run(connection)
        print 'Database setup completed. Now run the app without --setup.'
    except RqlRuntimeError:
        print 'App database already exists. Run the app without --setup.'
    finally:
        connection.close()

def requet(prenom, nom, email, message):
    rdb.db('thangui').table('message').insert([{ 'prenom' : prenom, 'nom' : nom, 'email' : email, 'message' : message}]).run(g.rdb_conn)

app = Flask(__name__)
app.config.from_object(__name__)

@app.before_request
def before_request():
    try:
        g.rdb_conn = rdb.connect(host=RDB_HOST, port=RDB_PORT, db=DB)
    except RqlDriverError:
        abort(503, "No database connection could be established.")

@app.teardown_request
def teardown_request(exception):
    try:
        g.rdb_conn.close()
    except AttributeError:
        pass

@app.route('/')
def accueil():
    return render_template('accueil.html')

@app.route('/contact/', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template('contact.html')
    else:
        if request.form["submit"] == "Envoyer":
            prenom = request.form['prenom']
            nom = request.form['nom']
            email = request.form['email']
            message = request.form['message']
            requet(prenom, nom, email, message)
            return render_template('contact.html', titre='Message envoye')

@app.route('/jeux/')
def nosjeux():
    return render_template('nosjeux.html')


if __name__ == '__main__':
    app.secret_key = '\xf8\xff\xbc\xfe\xde\x03\x8b\x81\xc9\x9c\xc4\xbe\x95\xa2\xf2'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)

