# Import things that will be needed.
import configparser
import urllib.request, urllib.parse
import json
import zipfile
from pathlib import Path

# Parse config.ini.
config = configparser.ConfigParser()
config.read('config.ini')

# Create download path if it doesn't exist.
downloadPath = Path(config['General']['Download Path'])
if not downloadPath.is_dir(): Path.mkdir(downloadPath)

# Setup Beat Saber playlist.
bspl = {
    "playlistTitle": config['Playlist']['Name'],
    "playlistAuthor": "BeatSaverPlaylistDownloader",
    "image": '',
    "songs": []
}

# Parse download list.
downloadList = open(config['General']['Playlist File']).read().strip().splitlines()

# Function to convert a string to a bool. I just wanna stay in base Python.
def strtobool(input): return input.lower() in ['y', 'yes', 't', 'true', 'on', '1']

# Function to verify map has difficulties required.
def checkDifficulty(mapDiffs):
    mapDiffs = mapDiffs['metadata']['difficulties']
    allDiffs = True
    for diff in mapDiffs:
        if strtobool(config['Difficulties'][diff]):
            if strtobool(config['Difficulties'][diff]) != mapDiffs[diff]: allDiffs = False
    return allDiffs

# Function to check if map is downloaded and if not, download it.
def downloadMap(map, dlMode):
    downloadPath = Path(config['General']['Download Path'] + map['key'] + ' - ' + map['name'] + '.zip')
    if downloadPath.is_file():
        print(dlMode + ' [Exists] Skipping Map: ' + map['name'])
    else:
        print(dlMode + ' Downloading Map: ' + map['name'])

        # Add http header to get around whatever is spitting a forbidden page.
        req = urllib.request.Request('https://beatsaver.com' + map['directDownload'])
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0')

        # Download map
        with urllib.request.urlopen(req) as dl:
            downloadPath.write_bytes(dl.read())

        # Add map to playlist file if enabled.
        if strtobool(config['Playlist']['Generate']):
            bspl['songs'].append({"hash": map['hash']})
            Path(config['General']['Download Path'] + config['Playlist']['Name'] + '.bplist').write_text(json.dumps(bspl))

# Loop through each song in the download list.
for songName in downloadList:
    print('\nSearching for Song: ' + songName)

    # Add http header to get around whatever is spitting a forbidden page.
    req = urllib.request.Request('https://beatsaver.com/api/search/text?q=' + urllib.parse.quote(songName))
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0')

    # Request the search results for the song's name and parse the json.
    with urllib.request.urlopen(req) as url:
        searchResults = json.loads(url.read().decode())['docs']

        # Download Modes
        if strtobool(config['Mode']['First Result']):
            if checkDifficulty(searchResults[0]):
                downloadMap(searchResults[0], '[FR]')
            else:
                print('[FR] [Diff] Skipping Map: ' + searchResults[0]['name'])

        if strtobool(config['Mode']['Most Downloads']):
            # Just set the map to download to the first so there's something to compare against.
            mapToDL = searchResults[0]
            for map in searchResults:
                if map['stats']['downloads'] > mapToDL['stats']['downloads']: mapToDL = map

            if checkDifficulty(mapToDL):
                downloadMap(mapToDL, '[DL]')
            else:
                print('[DL] [Diff] Skipping Map: ' + mapToDL['name'])

        if strtobool(config['Mode']['Most Upvotes']):
            # Just set the map to download to the first so there's something to compare against.
            mapToDL = searchResults[0]
            for map in searchResults:
                if map['stats']['upVotes'] > mapToDL['stats']['upVotes']: mapToDL = map

            if checkDifficulty(mapToDL):
                downloadMap(mapToDL, '[UV]')
            else:
                print('[UV] [Diff] Skipping Map: ' + mapToDL['name'])

        if strtobool(config['Mode']['Highest Rating']):
            # Just set the map to download to the first so there's something to compare against.
            mapToDL = searchResults[0]
            for map in searchResults:
                if map['stats']['rating'] > mapToDL['stats']['rating']: mapToDL = map

            if checkDifficulty(mapToDL):
                downloadMap(mapToDL, '[RT]')
            else:
                print('[RT] [Diff] Skipping Map: ' + mapToDL['name'])

# Auto unzip.
if strtobool(config['General']['Auto Unzip']):
    print('\nUnzipping maps...')
    for zip in downloadPath.iterdir():
        # Otherwise, it'll try to unzip the Beat Saber playlist.
        if '.zip' in str(zip):
            print('Unzipping ' + str(zip))
            extractPath = Path(str(zip).replace('.zip', '/'))
            zipfile.ZipFile(zip, 'r').extractall(path=extractPath)
            zip.unlink()