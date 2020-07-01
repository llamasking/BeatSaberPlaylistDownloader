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
downloadPath.mkdir(parents=True, exist_ok=True)

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

# Function to verify map has difficulties and game modes required.
def checkRequirements(map, dlMode):
    # Check map has all difficulties required
    mapDiffs = map['metadata']['difficulties']
    for diff in mapDiffs:
        if strtobool(config['Difficulties'][diff]):
            if strtobool(config['Difficulties'][diff]) != mapDiffs[diff]:
                print(dlMode + ' [Diff] Skipping Map: ' + map['name'])
                return False

    # Check if map has all modes required. WHY DOES THIS HAVE TO BE SO COMPLICATED?
    modesReq = 0
    modesHas = 0
    for cfgMode in config['Game Modes']:                        # Loop through each mode in the config.
        if strtobool(config['Game Modes'][cfgMode]):            # If the mode is marked as required,
            modesReq += 1                                       # Add one to the count of required modes.

    for mode in map['metadata']['characteristics']:             # Loop through each mode in the map.
        if strtobool(config['Game Modes'][mode['name']]):       # If the mode is listed as required in the config,
            modesHas += 1                                       # Add one to the count of modes the map has.

    if modesHas != modesReq:                                    # If the map doesn't have the modes required,
        print(dlMode + ' [Mode] Skipping Map: ' + map['name'])  # Say the map is being skipped,
        return False                                            # Then return False so that it isn't downloaded.

    # Return True if all difficulties and game modes required are there.
    return True

# Function to check if map is downloaded and if not, download it.
def downloadMap(map, dlMode):
    downloadPath = Path(config['General']['Download Path'] + map['key'] + ' - ' + map['name'] + '.zip')

    # Check if map was already downloaded.
    if downloadPath.is_file() or Path(config['General']['Download Path'] + map['key'] + ' - ' + map['name']).is_dir():
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

        if strtobool(config['Download Strategy']['First Result']):
            if checkRequirements(searchResults[0], '[FR]'):
                downloadMap(searchResults[0], '[FR]')

        if strtobool(config['Download Strategy']['Most Downloads']):
            # Just set the map to download to the first so there's something to compare against.
            mapToDL = searchResults[0]
            for map in searchResults:
                if map['stats']['downloads'] > mapToDL['stats']['downloads']: mapToDL = map

            if checkRequirements(mapToDL, '[DL]'):
                downloadMap(mapToDL, '[DL]')

        if strtobool(config['Download Strategy']['Most Upvotes']):
            # Just set the map to download to the first so there's something to compare against.
            mapToDL = searchResults[0]
            for map in searchResults:
                if map['stats']['upVotes'] > mapToDL['stats']['upVotes']: mapToDL = map

            if checkRequirements(mapToDL, '[UT]'):
                downloadMap(mapToDL, '[UV]')

        if strtobool(config['Download Strategy']['Highest Rating']):
            # Just set the map to download to the first so there's something to compare against.
            mapToDL = searchResults[0]
            for map in searchResults:
                if map['stats']['rating'] > mapToDL['stats']['rating']: mapToDL = map

            if checkRequirements(mapToDL, '[RT]'):
                downloadMap(mapToDL, '[RT]')

        if strtobool(config['Download Strategy']['All']):
            # Just download all the maps!
            for map in searchResults:
                if checkRequirements(mapToDL, '[All]'):
                    downloadMap(mapToDL, '[All]')

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