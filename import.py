# -*- coding: utf-8 -*-

import pysrt
import sys
import MySQLdb
import os
import re
import string
import argparse
import shutil

from whoosh.index import create_in, open_dir
from whoosh.fields import TEXT, NUMERIC, Schema

def addQuoteToSearch(id, quote):
    # extra checks, just to be sure
    quote = re.sub('<[^<]+?>', '', quote)
    quote = quote.replace('\n', ' ')
    quote = quote.strip()

    # remove punctuation, whitespace and make lowercase
    exclude = set(string.punctuation)
    quote = ''.join(ch for ch in quote if ch not in exclude)
    quote = quote.strip()
    quote = quote.lower()

    # add to search engine
    if quote.strip() != '':
        writer.add_document(quote=quote, reference=id)


#def addQuoteToDatabase(sub, ref, category):
def addQuoteToDatabase(id, part, mediaID, sub):
    txt = sub.text
    txt = re.sub('<[^<]+?>', '', txt)
    txt = txt.replace('\n', ' ')
    txt = txt.strip()

    start = toFfmpegTime(sub.start)
    end = toFfmpegTime(sub.end)

    cursor.execute('''INSERT INTO quotes (id, part, media, quote, start, end) VALUES (%s,%s,%s,%s,%s,%s)''', (id, part, mediaID, txt, start, end))


#def addCategoryToDatabase(refName, vidFile, name, image, description):
def addCategoryToDatabase(name, description, image, textID, mediaName, video, subtitle):
    cursor.execute('''SELECT * FROM categories WHERE textID=%s''', (textID,))
    res = cursor.fetchall()

    if len(res) > 1:
        print 'There are multiple matching categories in the db, wat?'
        sys.exit(0)

    if len(res) == 0:
        # new category, go and create it
        cursor.execute('''INSERT INTO categories (id, name, description, image, textID) VALUES (0,%s,%s,%s,%s)''', (name, description, image, textID))
        # start new quotes 0 (as it's a new category), and give the ID
        #return [0, cursor.lastrowid]
        categoryID = cursor.lastrowid
    else:
        categoryID = res[0]['id']

    # create the new entry in the media table
    cursor.execute('''INSERT INTO media (id, category, name, video, subtitle) VALUES (0,%s,%s,%s,%s)''', (categoryID, mediaName, video, subtitle))
    mediaID = cursor.lastrowid

    # return the category ID and media ID
    return [categoryID, mediaID]


def toFfmpegTime(time):
    startStr = ""
    startStr = startStr + str(time.hours).zfill(2) + ":"
    startStr = startStr + str(time.minutes).zfill(2) + ":"
    startStr = startStr + str(time.seconds).zfill(2) + "."
    startStr = startStr + str(time.milliseconds)
    return startStr

parser = argparse.ArgumentParser()
parser.add_argument('--subtitle', help='location of subtitle .srt file')
parser.add_argument('--video', help='location of subtitle video file')
parser.add_argument('--categoryname', help='name of the category (if new)')
parser.add_argument('--categoryimage', help='location of image thumbnail file')
parser.add_argument('--categorydescription', help='description of the film')
parser.add_argument('--name', help='name of the media')
args = parser.parse_args()

subFile = args.subtitle
vidFile = args.video
fullName = args.categoryname
thumbImage = args.categoryimage
description = args.categorydescription
mediaName = args.name



regex = re.compile('[^a-zA-Z]')
refName = regex.sub('', fullName).replace(' ', '').lower()
mediaRefName = regex.sub('', mediaName).replace(' ', '').lower()


if subFile == '' or vidFile == '' or fullName == '' or refName == '':
    print 'argument not found, please make sure all arguments are populated'
    sys.exit(0)

createCategory = not (thumbImage == '' or description == '')


# copy the files into appropriate folders
if (not os.path.isfile(subFile)) or (not os.path.isfile(vidFile)):
    print 'could not locate subtitle and/or video'
    sys.exit(0)
shutil.move(subFile, os.path.join(os.getcwd(), 'media/', (refName + '-' + mediaRefName + os.path.splitext(subFile)[1])))

#shutil.move(vidFile, os.path.join(os.getcwd(), 'media/', (refName + '-' + mediaRefName + os.path.splitext(vidFile)[1])))
vidSaveFile = os.path.join(os.getcwd(), 'media/', (refName + '-' + mediaRefName + '.mp4'))
os.system("ffmpeg -i \"" + vidFile + "\" -f mp4 -vcodec libx264 -preset fast -profile:v main -acodec aac -vf \"pad=ceil(iw/2)*2:ceil(ih/2)*2,scale=640:-1\" \"" + vidSaveFile + "\"")

subFile = os.path.join('media/', (refName + '-' + mediaRefName + os.path.splitext(subFile)[1]))
vidFile = os.path.join('media/', (refName + '-' + mediaRefName + '.mp4')
print subFile
print vidFile

if createCategory:
    if (not os.path.isfile(thumbImage)):
        print 'could not locate category thumb image'
        sys.exit(0)
    shutil.move(thumbImage, os.path.join(os.getcwd(), 'static/categories/', (refName + os.path.splitext(thumbImage)[1])))
    thumbImage = os.path.join('static/categories/', (refName + os.path.splitext(thumbImage)[1]))
    print thumbImage

# get the search engine, creating it if not already created
dbDir = os.path.join('searchdb/', refName)
if not os.path.exists(dbDir):
    if not createCategory:
        print 'please specify category description and image for new categories'
        sys.exit(0)
    os.makedirs(dbDir)
    schema = Schema(quote=TEXT(stored=True), reference=NUMERIC(stored=True))
    ix = create_in(dbDir, schema)
else:
    ix = open_dir(dbDir)
writer = ix.writer()


# database connection
db = MySQLdb.connect('127.0.0.1', 'quoteinsert', 'password', 'gifmaker')
cursor = db.cursor(MySQLdb.cursors.DictCursor)


# insert the category and media into the database
categoryID, mediaID = addCategoryToDatabase(fullName, description, thumbImage, refName, mediaName, vidFile, subFile)
#lastQuoteReference, categoryReference = addCategoryToDatabase(refName, vidFile, fullName, thumbImage, description)


# insert the quotes into the database and search engine
subs = pysrt.open(subFile)
i = 0
while i < len(subs):
    sub = subs[i]
    txt = sub.text

    # for quotes with multiple parts, each part has the same ID but a different part
    part = 0

    # reformat sub to single line
    txt = re.sub('<[^<]+?>', '', txt)
    txt = txt.replace('\n', ' ')
    txt = txt.strip()

    if 'opensubtitles.org' in txt.lower():
        i = i + 1
        continue

    # save to database
    #addQuoteToDatabase(sub, lastQuoteReference, categoryReference)
    addQuoteToDatabase(0, 0, mediaID, sub)
    id = cursor.lastrowid
    part = 1

    # process sub
    completeQuote = ""
    #while not (txt.endswith("'") or txt.endswith('"') or txt.endswith('!') or txt.endswith('?') or (txt.endswith('.') and not txt.endswith('...'))):
    while (not txt.endswith("'")) and (not txt.endswith('"')) and (not txt.endswith('!')) and (not txt.endswith('?')) and (not (txt.endswith('.') and not txt.endswith('...'))):
        # build up the whole quote

        # special case for quotes that start and end with ...
        if completeQuote.strip().endswith('...') and txt.strip().startswith('...'):
            completeQuote = completeQuote.strip() + " " + txt.strip()[3:]
        else:
            completeQuote = completeQuote.strip() + " " + txt.strip()

        # if at end, break
        i = i + 1
        if i >= len(subs):
            break

        # next part of the quote
        sub = subs[i]
        txt = sub.text
        txt = txt.replace('\n', ' ')
        txt = txt.strip()

        if 'opensubtitles.org' in txt.lower():
            i = i + 1
            continue

        # save to database
        #addQuoteToDatabase(sub, lastQuoteReference, categoryReference)
        addQuoteToDatabase(id, part, mediaID, sub)
        part = part + 1

    if completeQuote.strip().endswith('...') and txt.strip().startswith('...'):
        # special case for quotes that start and end with ...
        completeQuote = completeQuote.strip() + " " + txt.strip()[3:]
    else:
        completeQuote = completeQuote.strip() + " " + txt.strip()

    completeQuote = completeQuote.strip()

    # save to search engine
    addQuoteToSearch(id, completeQuote)

    # increment the counters
    i = i + 1


# commit the search engine and database
writer.commit()
db.commit()
