# -*- coding: utf-8 -*-

# script requires various dependencies, to install run:
#   pip install scikit-image pysrt
#   then install ffmpeg, imagemagick and opencv (with python lib support)

import logging
import json
import traceback
import random
import string
import newsearch
import shutil
import cv2
import datetime
import pysrt
import os
import time
import sys
import glob

from skimage.measure import compare_ssim as ssim
from websocket_server import WebsocketServer

reload(sys)
sys.setdefaultencoding('utf8')

def toFfmpegDuration(time, startTime):
    timeobj = datetime.datetime.strptime(time, '%H:%M:%S.%f').time()
    time = datetime.datetime.combine(datetime.date.min, timeobj) - datetime.datetime.min

    timeobj = datetime.datetime.strptime(startTime, '%H:%M:%S.%f').time()
    startTime = datetime.datetime.combine(datetime.date.min, timeobj) - datetime.datetime.min
    return time.total_seconds() - startTime.total_seconds()

def toFfmpegPreTime(time):
    pretime = toPreTime(time)

    m, s = divmod(pretime.total_seconds(), 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d.%02d" % (h, m, s, pretime.microseconds)

def toPreTime(time):
    timeobj = datetime.datetime.strptime(time, '%H:%M:%S.%f').time()
    t = datetime.datetime.combine(datetime.date.min, timeobj) - datetime.datetime.min
    pretime = t - datetime.timedelta(seconds=30)

    if (pretime.total_seconds() < 10):
        pretime = t - datetime.timedelta(seconds=0)

    return pretime

    m, s = divmod(pretime.total_seconds(), 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d.%02d" % (h, m, s, pretime.microseconds)

def toFfmpegEndTime(start, end):
    timeobj = datetime.datetime.strptime(start, '%H:%M:%S.%f').time()
    start = datetime.datetime.combine(datetime.date.min, timeobj) - datetime.datetime.min
    timeobj = datetime.datetime.strptime(end, '%H:%M:%S.%f').time()
    end = datetime.datetime.combine(datetime.date.min, timeobj) - datetime.datetime.min
    duration = end - start
    m, s = divmod(duration.total_seconds(), 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d.%02d" % (h, m, s, duration.microseconds)

def ffmpegPaletteCmd(settings):
    paletteCmd = "ffmpeg -y"
    paletteCmd = paletteCmd + " -i "    + settings['split']
    paletteCmd = paletteCmd + " -vf fps=" + str(settings['fps'])
    paletteCmd = paletteCmd + ",scale=" + str(settings['scale'])
    paletteCmd = paletteCmd + ":-1:flags=lanczos,palettegen=stats_mode=diff"
    paletteCmd = paletteCmd + " " + settings['palette']
    return paletteCmd

def ffmpegFramesCmd(settings):
    if os.path.isdir(settings['frameDir']):
        shutil.rmtree(settings['frameDir'])
    os.makedirs(settings['frameDir'])
    gifCmd = "ffmpeg -y"
    gifCmd = gifCmd + " -i "    + settings['split']
    gifCmd = gifCmd + " -i "    + settings['palette']
    gifCmd = gifCmd + " -filter_complex \""
    gifCmd = gifCmd + "fps=" + str(settings['fps'])
    gifCmd = gifCmd + ",scale=" + str(settings['scale'])
    gifCmd = gifCmd + ":-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle\""
    gifCmd = gifCmd + " -codec:a copy"
    gifCmd = gifCmd + " " + settings['frameDir'] + 'out%04d.png'
    return gifCmd

def ffmpegSplitCmd(quotes, startTime, endTime, videoFile, settings):
    #ffmpegPreSkipTime = toFfmpegPreTime(startTime)
    #preSkipTime = toPreTime(startTime)

    splitCmd = "ffmpeg -y"
    splitCmd = splitCmd + " -ss " + startTime # we can now do fast *and* accurate skip
    splitCmd = splitCmd + " -i " + videoFile
    #splitCmd = splitCmd + " -ss " + startTime # slower more accurate seek
    splitCmd = splitCmd + " -t " + toFfmpegEndTime(startTime, endTime)
    splitCmd = splitCmd + " -vf \""

    # there can be multiple quotes in the gif we need to make
    for quote in quotes:
        startDuration = toFfmpegDuration(quote['start'], startTime)
        endDuration = toFfmpegDuration(quote['end'], startTime)

        print startDuration
        print endDuration

        text = quote['text']
        fontSize = getFontSize(text, videoFile, settings)
        splitCmd = splitCmd + "drawtext=enable='between(t," + str(startDuration) + "," + str(endDuration) + ")':"
        splitCmd = splitCmd + "fontfile=./Quicksand-Bold.otf:"
        splitCmd = splitCmd + "fontcolor=white:"
        splitCmd = splitCmd + "fontsize=" + str(fontSize) + ":"
        splitCmd = splitCmd + "text='" + str(text.replace("'", '\xe2\x80\x99').replace('"', '\xe2\x80\x9d').replace('\n', ' ')) + "':"
        splitCmd = splitCmd + "x=(w-text_w)/2:"
        splitCmd = splitCmd + "y=((h-text_h)-20):"
        splitCmd = splitCmd + "borderw=2:bordercolor=black,"

    # add in the GIFless watermark
    splitCmd = splitCmd + "drawtext=fontfile=./Quicksand-Bold.otf:fontcolor=white:fontsize=20:text='GIFless':x=(w-text_w)-10:y=10:borderw=1:bordercolor=black\""
    splitCmd = splitCmd + " -codec:a copy"
    splitCmd = splitCmd + " " + settings['split']
    return splitCmd

def getPixelWidth(text, fontSize, videoFile, settings):
    pixelCmd = "ffmpeg -hide_banner"
    pixelCmd = pixelCmd + " -i " + videoFile
    pixelCmd = pixelCmd + " -vf drawtext=\""
    pixelCmd = pixelCmd + "fontfile=./Quicksand-Bold.otf:"
    pixelCmd = pixelCmd + "fontcolor=white:"
    pixelCmd = pixelCmd + "fontsize=" + str(fontSize) + ":"
    pixelCmd = pixelCmd + "text='" + str(text.replace("'", '\xe2\x80\x99').replace('"', '\xe2\x80\x9d').replace('\n', ' ')) + "':"
    pixelCmd = pixelCmd + "x=0+0*print(3.1415926)*print(tw):"
    pixelCmd = pixelCmd + "y=0+0*print(th):"
    pixelCmd = pixelCmd + "borderw=5:bordercolor=black:\""
    pixelCmd = pixelCmd + " -vframes 1"
    pixelCmd = pixelCmd + " -f null -"
    pixelCmd = pixelCmd + " 2>&1 | grep 3.14159 -A 2 | head -2 | tail -n 1"
    txtSize = int(float(os.popen(pixelCmd).read().strip()))
    return txtSize


def getBounds(text, fontSize, videoFile, settings):
    currentPixel = getPixelWidth(text, fontSize, videoFile, settings)

    tooBig = currentPixel > settings['videoWidth']
    print tooBig
    if tooBig:
        upperBound = fontSize
        lowerBound = upperBound
        #while currentPixel > settings['videoWidth']:
        while (currentPixel > settings['videoWidth']-20):
            temp = upperBound / 2
            currentPixel = getPixelWidth(text, temp, videoFile, settings)
            tooBig = (currentPixel > settings['videoWidth']-20)
            tooSmall = (currentPixel < settings['videoWidth']-80)
            suitable = (currentPixel < settings['videoWidth']-20 and currentPixel > settings['videoWidth']-80)
            if suitable:
                return (temp, temp)
            elif tooBig:
                upperBound = temp
            else:
                lowerBound = temp
        print (lowerBound, upperBound)
        print ((getPixelWidth(text, lowerBound, videoFile, settings)),(getPixelWidth(text, upperBound, videoFile, settings)))
        return (lowerBound, upperBound)
    return False


def getFontSize(text, videoFile, settings):
    bounds = getBounds(text, settings['maxFontSize'], videoFile, settings)

    if bounds == False:
        return settings['maxFontSize']

    lowerBound, upperBound = bounds

    if lowerBound == upperBound:
        return lowerBound

    while True:
        fontSize = (lowerBound + upperBound) / 2
        currentPixel = getPixelWidth(text, fontSize, videoFile, settings)
        print str(fontSize) + ":" + str(currentPixel)
        suitable = (currentPixel < settings['videoWidth']-100 and currentPixel > settings['videoWidth']-300)
        if suitable:
            return fontSize
        tooBig = currentPixel > settings['videoWidth']-100
        if tooBig:
            upperBound = fontSize
        else:
            lowerBound = fontSize


def getFrameDifferences(frames, startNum, endNum):
    print str(startNum) + ":" + str(endNum)
    print frames
    previous = cv2.imread(frames[startNum])
    for i in range((startNum+1), endNum+1):
        currentImage = frames[i]
        if not os.path.isfile(currentImage):
            break

        currentFrame = cv2.imread(currentImage)

        difference = ssim(previous, currentFrame, multichannel=True)
        previous = currentFrame

        print difference

        if difference < 0.4:
            print "change in scene between image " + frames[i-1] + " and " + frames[i]
            print "removing:"
            for j in range(i, endNum+1):
                print frames[j]
                os.remove(frames[j])


def removeFrames(settings):
    #frames = glob.glob(settings['frameDir'] + '*.png')
    #startFrame = len(frames)-5-1
    #endFrame = len(frames)-1
    #getFrameDifferences(frames[::-1], startFrame, endFrame)

    frames = glob.glob(settings['frameDir'] + '*.png')
    startFrame = len(frames)-5-1
    endFrame = len(frames)-1
    getFrameDifferences(frames, startFrame, endFrame)


def ffmpegGifCmd(settings):
    gifCommand = "ffmpeg -y"
    gifCommand = gifCommand + " -f image2"
    gifCommand = gifCommand + " -framerate " + str(settings['fps'])
    gifCommand = gifCommand + " -i " + settings['frameDir'] + "out%04d.png"
    gifCommand = gifCommand + " -i " + settings['palette']
    gifCommand = gifCommand + " -filter_complex \"scale=640:-1:flags=lanczos[x];[x][1:v]paletteuse\""
    gifCommand = gifCommand + " " + settings['output']
    return gifCommand
    #ffmpeg -f image2 -framerate 10 -i tmpFrames/out%04d.png -i palette.png -filter_complex "paletteuse" output7.gif


def new_message(client, server, message):
    print message

    try:
        data = json.loads(message)
    except:
        traceback.print_exc()
        print 'Unable to read json, exiting'
        server.send_message(client, '{"action":"error","status":"Unable to read websocket JSON"}')
        return

    quoteID = str(data['quote'])
    info = newsearch.getQuoteInfo(quoteID)
    videoFile = info['video']
    startTime = info['start']
    endTime = info['end']
    quotes = info['quotes']

    # create a random alphanumeric name for this gif
    randomName = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])

    # get the width of the video
    vid = cv2.VideoCapture( videoFile )
    videoWidth = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))

    settings = {
        'fps': 10,
        'scale': 640,
        'palette': 'tmp/' + randomName + 'palette.png',
        'split': 'tmp/' + randomName + 'split.mp4',
        'output': 'output/' + randomName + '.gif',
        'videoWidth': videoWidth,
        'maxFontSize': 52,
        'frameDir': 'tmp/' + randomName + 'frames/'
    }

    # extract from video, adding the text
    print "Extracting from video..."
    server.send_message(client, '{"action":"updateStatus","status":"Extracting from video and adding text..."}')
    split = ffmpegSplitCmd(quotes, startTime, endTime, videoFile, settings)
    os.system(split)
    print "\n\n\n"
    print split
    print "\n\n\n"

    # generate the GIF palette
    server.send_message(client, '{"action":"updateStatus","status":"Generating palate..."}')
    print "Generating palate..."
    genPalette = ffmpegPaletteCmd(settings)
    os.system(genPalette)
    print "\n\n\n"

    # create the frames
    server.send_message(client, '{"action":"updateStatus","status":"Generating frames..."}')
    print "Generating frames..."
    createFrames = ffmpegFramesCmd(settings)
    os.system(createFrames)
    print "\n\n\n"

    # remove erroniuos frames
    #server.send_message(client, '{"action":"updateMsg","msg":"Removing Erroneous Frames..."}')
    #print "Removing Erroneous Frames..."
    #removeFrames(settings)

    # combine frames into gif
    server.send_message(client, '{"action":"updateStatus","status":"Combining frames to gif..."}')
    print "Combining frames to gif..."
    createGif = ffmpegGifCmd(settings)
    os.system(createGif)
    print "\n\n\n"

    # send the finished gif to the client
    server.send_message(client, '{"action":"finished","url":"/gif/' + randomName + '.gif' + '"}')

    # clean up the tmp files
    shutil.rmtree(settings['frameDir'])
    os.remove(settings['palette'])
    os.remove(settings['split'])

server = WebsocketServer(8000, host='', loglevel=logging.INFO)
server.set_fn_message_received(new_message)
server.run_forever()
