// Load things
const fs = require('fs');
const http = require('https');
const config = require('./config.json');
const playlist = fs.readFileSync(config.downloadFile).toString().split('\n');

// Lets go generate a playlist file while we're at it!
const bspl = {
    playlistTitle: config.playlistName,
    playlistAuthor: 'BeatSaverPlaylistDownloader',
    image: 'data:image/png;base64,' + fs.readFileSync(config.playlistPNG, 'base64'),
    songs: [],
};

// Run for each song listed in the playlist file.
function searchSong(songName) {
    return new Promise(function (resolve, reject) {
        // Options to get around cloudflare or whatever is throwing 403.
        const options = {
            host: 'beatsaver.com',
            path: '/api/search/text?q=' + escape(songName),
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0',
            },
        };

        // Pull search results from the API
        http.get(options, function (response) {
            var body = '';

            response.on('data', function (chunk) {
                body += chunk;
            });

            response.on('end', function () {
                if (response.statusCode === 200) {
                    resolve(JSON.parse(body));
                } else {
                    reject(response.statusCode);
                }
            });
        });
    });
}

// Function to download songs.
function downloadSong(song, songName) {
    var hasAllDifficulties = true;
    // There's probably a faster/better way to do this that I just don't know.
    if (config.requiredDifficulties.easy && !song.metadata.difficulties.easy) hasAllDifficulties = false;
    if (config.requiredDifficulties.normal && !song.metadata.difficulties.normal) hasAllDifficulties = false;
    if (config.requiredDifficulties.hard && !song.metadata.difficulties.hard) hasAllDifficulties = false;
    if (config.requiredDifficulties.expert && !song.metadata.difficulties.expert) hasAllDifficulties = false;
    if (config.requiredDifficulties.expertPlus && !song.metadata.difficulties.expertPlus) hasAllDifficulties = false;

    // Check if the song has all the difficulties needed.
    if (hasAllDifficulties) {
        // Check if the file is already downloaded. If so, skip.
        if (fs.existsSync(`./downloads/${song.key} - ${song.name}.zip`)) {
            console.log(`"${song.key} - ${song.name}" for "${songName} already exists and was skipped."`);
        } else {
            // Things with the playlist file
            bspl.songs.push({ hash: song.hash });
            fs.writeFileSync(`./downloads/${config.playlistName}.bplist`, JSON.stringify(bspl, null, 2));

            // Options to get around cloudflare or whatever is throwing 403.
            const options = {
                host: 'beatsaver.com',
                path: song.directDownload,
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0',
                },
            };

            const file = fs.createWriteStream(`./downloads/${song.key} - ${song.name}.zip`);
            http.get(options, (response) => {
                response.on('data', (chunk) => {
                    file.write(chunk);
                });

                response.on('end', () => {
                    file.close();
                });

                response.on('error', () => {
                    // Just delete the file because I otherwise don't give a shit.
                    fs.unlink(`./downloads/${song.key} - ${song.name}.zip`);
                });
            });
        }
    } else {
        console.log(`Map "${song.key} - ${song.name}" for ${songName} does not have the required difficulties and was skipped.`);
    }
}

// Main function
function main(songName) {
    searchSong(songName).then((searchResults) => {
        // Just to prevent an error with Most* download modes
        var song = searchResults.docs[0];

        // Check for each download mode. If multiple download modes are enabled, use multiple.
        // Get the first song in the search results.
        if (config.downloadMode.FirstResult) {
            // Download the song
            console.log(`Downloading the first result for "${songName}"`);
            downloadSong(song, songName);
        }

        // Get the song with the most downloads in the search results.
        if (config.downloadMode.MostDownloads) {
            // Go through each song in search results and make the song with the most downlads 'song'
            searchResults.docs.forEach((thisSong) => {
                if (thisSong.stats.downloads > song.stats.downloads) song = thisSong;
            });

            // Download the song
            console.log(`Downloading map with most downloads for "${songName}"`);
            downloadSong(song, songName).then();
        }

        // Get the song with the most upvotes in the search results.
        if (config.downloadMode.MostUpvotes) {
            // Go through each song in search results and make the song with the most downlads 'song'
            searchResults.docs.forEach((thisSong) => {
                if (thisSong.stats.upVotes > song.stats.upVotes) song = thisSong;
            });

            // Download the song
            console.log(`Downloading map with most upvotes for "${songName}"`);
            downloadSong(song, songName).then();
        }
    });
}

// Just start downloads on a delay because IM SO FUCKING DONE
var i = 0;
setInterval(() => {
    if (i < playlist.length - 1) {
        i++;
        main(playlist[i]);
    }
}, 1000 * config.downloadDelay);
// Run once now, otherwise it takes one cycle to start downloading.
main(playlist[0]);
