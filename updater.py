#!/usr/bin/python
import requests, json, os

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

directory_list = {}
file_list = []
basepath = os.getcwd()
count = 0
total = len(build_files)
for file in build_files:
    filepath = os.path.join(basepath, "game", file['RelativePath'])
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)

    downloadurl = f'{buildsite_url}{latest_build}/Game/{file["RelativePath"]}'
    count += 1
    print(f'Downloading ({count}/{total}) {downloadurl} ...')
    download_response = requests.get(downloadurl, headers=headers)
    open(filepath, 'wb').write(download_response.content)

print("Done!")
