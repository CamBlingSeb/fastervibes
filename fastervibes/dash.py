from __future__ import unicode_literals
import os
import youtube_dl
from flask import (
    Blueprint, current_app, redirect, render_template, request, flash, send_from_directory
)

from fastervibes.db import get_db

bp = Blueprint('dash', __name__, url_prefix='/dash')

class MyLogger(object):
    def debug(self, msg):
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        print(msg)

@bp.route('/', methods=('GET', 'POST'))
async def dash():
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

    return render_template('dash.html.j2')

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

    def my_hook(d):
        if d['status'] == 'downloading':
            return render_template('downloading.html.j2',
                downloadedBytes=d['downloaded_bytes'],
                totalBytes=d['total_bytes'],
                eta=d['eta'],
                elapsed=d['elapsed'],
                speed=d['speed']
            )
        elif d['status'] == 'finished':
            print('Done Downloading to Server... now Converting')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'outtmpl': os.path.join(current_app.root_path, 'media/%(title)s.%(ext)s'),
        'addmetadata': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': fileFormat,
            'preferredquality': '192',
        },
        {
            'key': 'FFmpegMetadata'
        }],
        'nocheckcertificate': True,
        'logger': MyLogger(),
        'progress_hooks': [my_hook]
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