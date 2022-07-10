from __future__ import unicode_literals
import os
import youtube_dl
from flask import (
    Blueprint, current_app, redirect, render_template, request, flash, send_from_directory
)
# import ffmpeg

from fastervibes.db import get_db

bp = Blueprint('index', __name__)

class MyLogger(object):
    def debug(self, msg):
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        print(msg)

@bp.route('/', methods=('GET', 'POST'))
async def index():
    if request.method == 'POST':
        url = request.form['url']
        error = None

        if url is None:
            error = 'Please provide a URL'
        else:
            info = await getVideoInfo(url)
            if info is None:
                pass
            else:
                # print('Thumbnails: ', info['thumbnails'])
                return render_template(
                    'video-data.html.j2',
                    url=url, 
                    videoTitle=info['title'], 
                    thumbnail=info['thumbnails'][0]
                )
        flash(error)

    return render_template('home.html.j2')
    


async def getVideoInfo(url):
    info = await fetchVideoInfo(url)
    if info is None:
        pass
    else:
        return info
    
async def fetchVideoInfo(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'nocheckcertificate': True,
        'logger': MyLogger()
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print('Starting Request')
        info = ydl.extract_info(url, download = False)
        # print('Finished Request for: ', info)
        print('Finished Request')
        if info is None:
            print('No Data')
            return
        else:
            print('Name: ', info['title'])
            return info


@bp.post('/convert')
def convert():
    url = request.form['url']
    title = request.form['title']
    fileFormat = request.form['output-format']
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(current_app.root_path, 'media/%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'nocheckcertificate': True,
        'logger': MyLogger()
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print('Starting Request')
        ydl.download([url])

    return render_template(
        'download.html.j2',
        filename="%s.%s" % (title, fileFormat)
    )


@bp.post('/download')
def download():
    print('Attempting Download...')
    filename = request.form['filename']
    mediapath = os.path.join(current_app.root_path,'media')
    return send_from_directory(mediapath, filename, as_attachment=True)
