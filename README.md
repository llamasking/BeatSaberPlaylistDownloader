# BeatSaverPlaylistDownloader

Please god end me I spent lke half a day making this and all of that was fighting with http. At the end I just gave up and made it loop every few seconds to have at least some delay downloading the files but FUCK ME.

## How do you use it?

1. Give it a text file with the name of each song you want to download on it's own line.

```
song1
someone - song2
song3 (kill me remix)
...
```

2. Fill out config.json with important info such as, the location of the file mentioned above (downloadFile), what you want to download, and any difficulty requirements, how long to wait between starting each download, and, for Beat Saber's in-game playlists, the playlist icon (png) and name.

3. Run download.js in NodeJS. Everything will be in the "downloads" folder.
