from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from moviepy.editor import * 
from .models import Video
from .serializers import VideoSerializer
from django.conf import settings 
import os
from django.utils.datastructures import MultiValueDictKeyError
import requests
import shutil

# from videoApp.views import getVideoName
# getVideoName(get)

# get video filename function
def getVideoName(url):
    return url.split("/")[-1] 

def downloadFile(AFileName):
    try: 
        # extract file name from AFileName
        filename = AFileName.split("/")[-1] 
        # download image using GET
        # exception handling 
        rawImage = requests.get(AFileName, stream=True)

        # get the path in the static folder
        path = os.path.join(settings.BASE_DIR, 'static/{name}'.format(name = filename))
        
        # save the image recieved into the file
        with open(path, 'wb') as fd:
            for chunk in rawImage.iter_content(chunk_size=1024):
                fd.write(chunk)
        return True
    except: 
        return False

def getProps(request):
    try: 
        video_url = request.GET['url']
        start_time = int(request.GET['start'])
        end_time = int(request.GET['end'])

        return [video_url, start_time, end_time]
    except MultiValueDictKeyError as error: 
        return False
        
def moveFile(video_url):
    filename = getVideoName(video_url)
    desired_url = os.path.join(settings.BASE_DIR, 'static/{name}'.format(name = filename))
    # desired_url = "/Users/zhaniya/Desktop/trimVideo/videoProject/static/{name}".format(name = filename)
    try: 
        shutil.copyfile(video_url, desired_url)
        return True
    except FileNotFoundError: 
        return False

def validateTime(start_time, end_time):
    try: 
        return [int(start_time), int(end_time)]
    except:
        return False 


def trimClip(filename, start, end):
    try:
        video = VideoFileClip('static/{name}'.format(name=filename)).subclip(start,end)
        return video
    except: 
        return False

def writeEditedVideo(filename, video):
    media_url = os.path.join(settings.BASE_DIR, 'media/videos/{name}'.format(name = filename)) 
    video.write_videofile(media_url)
    return media_url

class TrimLocally(View):
    def get(self, request, *args, **kwargs):
        props = getProps(request)
        if(props == False): 
            return JsonResponse({'error':"you miss one of the params ['url', 'start_time', 'end_time'"})
        else: 
            video_url = props[0]
            start_time = props[1]
            end_time = props[2]

        if(moveFile(video_url) == False):
            error = 'no video was found in: {url}'.format(url = video_url)
            return JsonResponse({'error' : error})
        
        timeArray = validateTime(start_time, end_time)
        if(timeArray == False):
            return JsonResponse({'error':'your time input is not integer'})
        else:
            start = timeArray[0]
            end = timeArray[1]
    
        filename = getVideoName(video_url)
        video = trimClip(filename, start, end)
        if(video == False):
            return JsonResponse({'error': 'start or end time exceeds the video duration'})
        
        media_url = writeEditedVideo(filename, video)

        return JsonResponse({'media_url': media_url})


class TrimInternet(View):
    def get(self, request, *args, **kwargs):
        props = getProps(request)
        if(props == False): 
            return JsonResponse({'error':"you miss one of the params ['url', 'start_time', 'end_time'"})
        else: 
            video_url = props[0]
            start_time = props[1]
            end_time = props[2]

        timeArray = validateTime(start_time, end_time)
        if(timeArray == False):
            return JsonResponse({'error':'your time input is not integer'})
        else:
            start = timeArray[0]
            end = timeArray[1]

        videoFound = downloadFile(video_url)
        if(videoFound == False):
            return JsonResponse({'error': 'the video was not found. Please check the uri'})

        filename = getVideoName(video_url)
        video = trimClip(filename, start, end)
        if(video == False):
            return JsonResponse({'error': 'start or end time exceeds the video duration'})
        
        media_url = writeEditedVideo(filename, video)

        return JsonResponse({'media_url': media_url})

