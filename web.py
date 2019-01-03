# -*- coding: utf-8 -*-

import bottle
import socket
import json
import struct
import search


@bottle.route('/search/<category>/<query>/<counter>')
@bottle.route('/search/<category>/<query>/<counter>/')
def search(category, query, counter):
    # form the json to send to the search server
    results = search.quoteSearch(category, query)

    returnResult = {}
    returnResult['counter'] = counter
    returnResult['results'] = results
    returnResult = json.dumps(returnResult)
    return returnResult

# static files (js/css/etc)
@bottle.route('/static/<filepath:path>')
def static(filepath):
    return bottle.static_file(filepath, root='static/')

# created gifs
@bottle.route('/gif/<filepath:path>')
def static(filepath):
    return bottle.static_file(filepath, root='output/')


@bottle.route('')
@bottle.route('/')
@bottle.route('index')
@bottle.route('/index')
@bottle.route('/index.html')
@bottle.route('index.html')
def index():
    # form the json to send to the search server
    results = search.categoryIndex()
    return bottle.template('index', films=results)


@bottle.route('/category/<name>')
@bottle.route('/category/<name>/')
def category(name):
    data = search.getCategoryInfo(name)
    return bottle.template('category', category=data, films={})


@bottle.route('/generate/<category>/<quote>')
@bottle.route('/generate/<category>/<quote>/')
def category(category, name):
    data = search.getCategoryInfo(name)
    return bottle.template('category', category=data, films={})

bottle.run(host='', port=8080)
