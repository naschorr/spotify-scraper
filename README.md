# spotify-scraper
A Python API for getting the artist, song, and album art for the currently playing Spotify song. Requires Windows.

![example usage gif](https://raw.githubusercontent.com/naschorr/spotify-scraper/master/resources/spotify_scraper_demo.gif)
> An example of the `print_song.py` script running.

### Installation
Clone the repo wherever you'd like, then run `pip install -r requirements.txt` from the repo's root directory. Then, take a look at the `examples/` folder to see it in action.

### API
#### Instantiation
Usage of the scraper requires an import of SpotifyScraper. For example, `from spotify_scraper import SpotifyScraper`.
After that, you've got two main choices for instantiation. Either you can instantiate with a callback function such as: `scraper = SpotifyScraper(callback)`, or you can do it without a callback function like so: `scraper = SpotifyScraper()`. Any kwargs you may want to use can also be tacked onto the end of the call, as you'd expect.

The instantiation using callbacks works by calling your supplied callback function every time the song changes, while the non-callback version doesn't, and assumes that you'll manually call the `updateSongData(callback=None)` method, and manually access the attributes that you want.

##### Callbacks
Your supplied callback function needs to either take no arguments, or one argument (not counting the `self` argument). If it takes one argument, then SpotifyScraper will pass a dictionary (see `getSongDataDict()` definition in the Methods section) containing the attributes that your callback can handle. If it takes no arguments, then you can think of the callback as more of an event, and you'll have to manually get the attributes yourself when it's called.

##### Kwargs
Currently, SpotifyScraper can take the following kwargs:
- `shouldGetArt` - Boolean - Indicates that it should or shouldn't capture album art.
- `artSideLength` - Int - The height and width (pixels) of the square album art capture region. (ex. 400 would refer to a height of 400px and a width of 400px) 
- `artOffsets` - (Int, Int) - he offset from the left side of the Spotify window, and the offset from the bottom of the window for the bottom left corner of the album art.

#### Attributes
- `song` - String - Holds the currently playing song's name, or the most recently played song's name if an ad is playing.
- `artist` - String - Holds the currently playing song's artist, or the most recently played song's artist if an ad is playing.
- `art` - PIL.Image - Holds the currently playing song's album art, or the most recently played song's art if an ad is playing.
- `windowHandle` - Int - Holds the window handle of the Spotify window being scraped.

#### Methods
- `stopScraping()` - Sets a flag that will end the scraper thread. Returns nothing.
- `playSong()` - Simulates media key presses to start the current song from the beginning. Returns nothing.
- `updateWindowHandle(callback=None)` - Searches for and updates the scraper with the Spotify windows' window handle.
- `captureAlbumArt()` - Pulls the Spotify window to the foreground, maximizes it, and then takes a screenshot of the region defined by `self.artSideLength`. The screenshot is then stored in the `art` attribute. Returns nothing.
- `updateSongData(callback=None)` - Updates the `song`, `artist`, and `art` attributes if they're different than those of the currently playing song. Returns nothing.
- `getSongDataDict()` - Returns a dictionary containing the `song`, `artist`, and `art` attributes like so: `{"song":"song's name", "artist":"artist's name", "art":<song's album art as PIL.Image object>}.`
- `getSongKey()` - Returns a string containing the key used to retrive the song's name from the dictionary above.
- `getArtistKey()` - Returns a string containing the key used to retrive the artist's name from the dictionary above.
- `getArtKey()`- Returns a string containing the key used to retrive the song's album art from the dictionary above.

### Configuration
#### Strings
In the source `spotify_scraper.py` file, the following string literals can be tweaked to suit your needs:
- `SPOTIFY` - The string "spotify", used to help find the Spotify processes when updating the window handle.
- `GET_ART` - The name of the kwarg that the SpotifyScraper constructor takes to indicate that it should or shouldn't capture album art.
- `ART_SIDE_LENGTH` - The name of the kwarg that the SpotifyScraper constructor takes to specify the height and width (pixels) of the album art region to capture.
- `ART_WINDOW_OFFSET` - The name of the kwarg that the SpotifyScraper constructor takes to specify the left and bottom pixel offsets of the album art region to capture.
- `SONG` - The name of the key used to retrive the song's name from the `getSongDataDict()` dictionary above.
- `ARTIST` - The name of the key used to retrive the artist's name from the `getSongDataDict()` dictionary above.
- `ART` - The name of the key used to retrive the song's album art from the `getSongDataDict()` dictionary above.

#### Configs
Below the string literals, there are also some configs that you may wish to change. I'll probably end up making these configurable from kwargs used when instantiating the class.
- `WAIT_TIME` - Int - The default time (seconds) to wait between actions that can take a bit of time (ex. the time between maximizing the Spotify window, and taking a screenshot of the album art).
- `ATTEMPT_LIMIT` - Int - The number of attempts that should be made to find an active Spotify Window before giving up.
- `SHORT_WAIT` - Int/Float - The time (seconds) that the scraper thread should wait before trying to update the song attributes.
- `SONG_DATA_RE` - The compiled regex pattern used to scrape song and artist data from the Spotify window's title bar.
- `ALBUM_ART_SIZE` - Int - The height and width (pixels) of the album art capture region.
- `ALBUM_ART_OFFSET` - (Int, Int) - The offset from the left side of the Spotify window, and the offset from the bottom of the window for the bottom left corner of the album art.
