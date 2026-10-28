"""YouTube uploader for the channel autopilot (Python standard library only).

  python3 upload.py list                  -> past uploads, newest first: "title | first line of description"
  python3 upload.py video.mp4 meta.json   -> uploads the video, prints its URL

meta.json: {"title": "...", "description": "...", "tags": ["..."]}
Needs the environment variables YT_CLIENT_ID, YT_CLIENT_SECRET and YT_REFRESH_TOKEN (see README.md).
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API = 'https://www.googleapis.com/youtube/v3'
UPLOAD = 'https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status'


def call(url, data=None, headers=None, method=None):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    with urllib.request.urlopen(req, timeout=600) as r:
        return r.headers, r.read()


def token():
    body = urllib.parse.urlencode({
        'client_id': os.environ['YT_CLIENT_ID'], 'client_secret': os.environ['YT_CLIENT_SECRET'],
        'refresh_token': os.environ['YT_REFRESH_TOKEN'], 'grant_type': 'refresh_token'}).encode()
    return json.loads(call('https://oauth2.googleapis.com/token', body)[1])['access_token']


def get(tok, path, **query):
    url = f'{API}/{path}?{urllib.parse.urlencode(query)}'
    return json.loads(call(url, headers={'Authorization': 'Bearer ' + tok})[1])


def past_uploads(tok):
    # shortcut: last 50 uploads only, enough to avoid repeats; page with nextPageToken if the playbook needs more
    ch = get(tok, 'channels', part='contentDetails', mine='true')['items'][0]
    uploads = ch['contentDetails']['relatedPlaylists']['uploads']
    items = get(tok, 'playlistItems', part='snippet', playlistId=uploads, maxResults=50).get('items', [])
    return [f"{i['snippet']['title']} | {i['snippet']['description'].split(chr(10))[0]}" for i in items]


def upload(tok, video, meta):
    body = {
        'snippet': {'title': meta['title'][:100], 'description': meta['description'][:5000],
                    'tags': meta.get('tags', []), 'categoryId': '1'},  # 1 = Film & Animation
        'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False},
    }
    headers, _ = call(UPLOAD, json.dumps(body).encode(), {
        'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json; charset=UTF-8',
        'X-Upload-Content-Type': 'video/mp4', 'X-Upload-Content-Length': str(os.path.getsize(video))})
    with open(video, 'rb') as f:
        _, b = call(headers['Location'], f.read(), {'Authorization': 'Bearer ' + tok, 'Content-Type': 'video/mp4'}, 'PUT')
    return json.loads(b)


def main(args):
    missing = [k for k in ('YT_CLIENT_ID', 'YT_CLIENT_SECRET', 'YT_REFRESH_TOKEN') if not os.environ.get(k)]
    if missing:
        sys.exit(f'missing environment variables: {", ".join(missing)} (see youtube-channel/README.md)')
    try:
        tok = token()
        if args[:1] == ['list']:
            print('\n'.join(past_uploads(tok)))
        elif len(args) == 2:
            v = upload(tok, args[0], json.load(open(args[1])))
            print(f"https://youtube.com/shorts/{v['id']} ({v['status']['privacyStatus']})")
        else:
            sys.exit(__doc__)
    except urllib.error.HTTPError as e:
        sys.exit(f'YouTube API error {e.code}: {e.read().decode(errors="replace")}')


if __name__ == '__main__':
    main(sys.argv[1:])
