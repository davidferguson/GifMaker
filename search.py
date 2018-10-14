# -*- coding: utf-8 -*-

import sys
import MySQLdb
import os
import re
import string

from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser

# database connection
db = MySQLdb.connect('127.0.0.1', 'quotesearch', 'password', 'gifmaker')
cursor = db.cursor(MySQLdb.cursors.DictCursor)

def performSearch(category, txt):
    dbDir = os.path.join('searchdb/', category)
    if not os.path.exists(dbDir):
        print 'Error: the category name does not exist'
        sys.exit(0)

    ix = open_dir(dbDir)
    searcher = ix.searcher()

    #remove html, newlines and whitespace
    txt = re.sub('<[^<]+?>', '', txt)
    txt = txt.replace('\n', ' ')
    txt = txt.strip()

    # remove punctuation, whitespace and make lowercase
    exclude = set(string.punctuation)
    txt = ''.join(ch for ch in txt if ch not in exclude)
    txt = txt.strip()
    txt = txt.lower()

    query = QueryParser('quote', ix.schema).parse(txt)
    res = searcher.search(query)

    if len(res) == 0:
        # okay, begin the long but more effective search
        pass

    return res


def mapSearchToQuote(category, ref):
    # get the category
    cursor.execute('''SELECT * FROM categories WHERE textID=%s''', (category,))
    res = cursor.fetchall()

    if len(res) != 1:
        print 'Couldn\'t get category in database, exiting'
        sys.exit(0)

    categoryId = res[0]['id']


    # get the quote
    print "SELECT * FROM quotes WHERE id=" + str(ref) + " ORDER BY part ASC"
    cursor.execute('''SELECT * FROM quotes WHERE id=%s ORDER BY part ASC''', (ref,))
    res = cursor.fetchall()

    if len(res) == 0:
        print 'Quote does not appear to exist in the database'
        sys.exit(0)

    completeQuote = res[0]['quote']
    startTime = res[0]['start']
    mediaID = res[0]['media']

    cursor.execute('''SELECT * FROM media WHERE id=%s''', (mediaID,))
    media = cursor.fetchall()

    if len(media) == 0:
        print 'Media does not appear to exist in the database'
        sys.exit(0)

    mediaName = media[0]['name']

    for i in range(1, len(res)):
        quote = res[i]['quote']

        if completeQuote.strip().endswith('...') and quote.strip().startswith('...'):
            completeQuote = completeQuote.strip() + " " + quote.strip()[3:]
        else:
            completeQuote = completeQuote.strip() + " " + quote.strip()

    return (completeQuote, startTime, mediaName)


def quoteSearch(category, query):
    category = str(category).strip()
    query = str(query).strip()

    # check that the query parts contain something
    if (category == '') or (query == ''):
        print 'Blank options in query, exiting'
        #client.sendall('[]')
        return []

    # check category exists
    cursor.execute('''SELECT * FROM categories WHERE textID=%s''', (category,))
    res = cursor.fetchall()
    if len(res) != 1:
        # we were expecting one result, but we didn't get it. send back nothing
        print 'Didnt get one category, exiting'
        return []

    # and now we can actually run the search!
    quotes = []
    results = performSearch(category, query)
    print results
    for result in results:
        quote = {}
        quote['quote'], quote['start'], quote['media'] = mapSearchToQuote(category, result['reference'])
        quote['id'] = result['reference']
        quotes.append(quote)

    # send the search results back
    return quotes


def categoryIndex():
    # check category exists
    cursor.execute('''SELECT * FROM categories''', [])
    res = cursor.fetchall()
    if len(res) == 0:
        # we were expecting one result, but we didn't get it. send back nothing
        print 'no categories found, exiting'
        #client.sendall('[]')
        return []

    categories = []
    index = 0
    for row in res:
        category = {}
        category['name'] = row['name']
        category['image'] = row['image']
        category['description'] = row['description']
        category['category'] = row['textID']
        category['index'] = index
        categories.append(category)
        index = index + 1

    # send the search results back
    return categories


def getCategoryInfo(reference):
    cursor.execute('''SELECT * FROM categories WHERE textID=%s''', (reference,))
    res = cursor.fetchall()
    if len(res) != 1:
        print 'category not found, exiting'
        return []

    res = res[0]
    data = {}
    data['name'] = res['name']
    data['image'] = res['image']
    data['description'] = res['description']
    data['reference'] = reference

    # send the search results back
    return data


def getQuoteInfo(quoteID):
    cursor.execute('''SELECT * FROM quotes WHERE id=%s ORDER BY part ASC''', (quoteID,))
    quotes = cursor.fetchall()
    if len(quotes) == 0:
        print 'Could not get quote'
        return []

    # get the media - will be the same across all parts
    mediaID = quotes[0]['media']
    print mediaID
    cursor.execute('''SELECT * FROM media WHERE id=%s''', (mediaID,))
    media = cursor.fetchall()
    if len(media) != 1:
        print 'Could not get media for quote'
        return {}
    mediaFile = media[0]['video']

    # build up the return object
    res = {}
    res['video'] = mediaFile
    res['start'] = quotes[0]['start']
    res['end'] = quotes[len(quotes)-1]['end']
    res['quotes'] = []
    for quote in quotes:
        quoteRes = {}
        quoteRes['start'] = quote['start']
        quoteRes['end'] = quote['end']
        quoteRes['text'] = quote['quote'].replace(':',',').replace(';',',')
        res['quotes'].append(quoteRes)

    return res
