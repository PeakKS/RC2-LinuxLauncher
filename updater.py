#!/usr/bin/python
import requests, json, os
import sqlite3 as sql
from datetime import datetime as timeconv
import datetime

buildsite_url = 'https://patcher-production.robocraft.org/Builds/'

#Need to fake headers or Cloudflare will get mad at us
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'cross-site',
}

buildlist_response = requests.get(buildsite_url + 'builds_index.json', headers=headers)
buildlist = json.loads(buildlist_response.text)
print(f'Found {len(buildlist)} builds')
latest_build = buildlist['AvailableBuilds'].pop(-1)

print(f'Attempting to download latest build "{latest_build}"')
build = requests.get( buildsite_url + 'build_' + latest_build + '.json')
build_files = json.loads(build.text)['Entries']

db = sql.connect('updater.db')
cur = db.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS TIMESTAMPS (
        path TEXT UNIQUE,
        timestamp TEXT
    )
""")

basepath = os.getcwd()
count = 0
total = len(build_files)
for file in build_files:
    filepath = os.path.join(basepath, "game", file['RelativePath'])
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)

    cur.execute(f'INSERT INTO TIMESTAMPS (path, timestamp) VALUES ("{file["RelativePath"]}", "{file["LastWriting"]}")')
    cur.execute(f'SELECT timestamp from TIMESTAMPS WHERE path = "{file["RelativePath"]}"')
    current_file_time = cur.fetchall()[0][0]
    local = timeconv.strptime(current_file_time, "%Y-%m-%d %H:%M:%SZ")
    remote = timeconv.strptime(file["LastWriting"], "%Y-%m-%d %H:%M:%SZ")
    difference = remote - local

    count += 1
    downloadurl = f'{buildsite_url}{latest_build}/Game/{file["RelativePath"]}'
    if difference > datetime.timedelta(minutes=0) or not os.path.isfile(filepath):
        print(f'Downloading ({count}/{total}) {downloadurl} ...')
        download_response = requests.get(downloadurl, headers=headers)
        open(filepath, 'wb').write(download_response.content)
    else:
        print(f'Skipping ({count}/{total}) {downloadurl} ... Up To Date')

print("Done!")
