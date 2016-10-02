import threading
import queue
import re
import psutil
import pyscreenshot
import time
from PIL import Image
from win32con import SW_SHOWMAXIMIZED
from win32gui import GetWindowText, EnumWindows, GetForegroundWindow, SetForegroundWindow, ShowWindow, GetWindowRect
from win32process import GetWindowThreadProcessId
from win32api import MapVirtualKey, keybd_event

## String Literals
SPOTIFY = "spotify"
GET_ART = "shouldGetArt"
ART_SIDE_LENGTH = "artSideLength"
ART_WINDOW_OFFSET = "artOffsets"
SONG = "song"
ARTIST = "artist"
ART = "art"

## Configs
WAIT_TIME = 1
ATTEMPT_LIMIT = 5
SHORT_WAIT = 0.001
SONG_DATA_RE = re.compile(r'(.+) - (.+)')

## Define capture regions and offsets (These should play nice with 1080p screens)
ALBUM_ART_SIZE = 400			# 400px^2
ALBUM_ART_OFFSET = (8, 119)		# (Offset from left side of window, Offset from bottom of window)

class SpotifyScraper:

	def __init__(self, callback=None, **kwargs):
		self.windowHandle = None
		self.callback = callback
		self.song = None
		self.artist = None
		self.art = None
		self.shouldGetArt = kwargs[GET_ART] if GET_ART in kwargs else False
		self.artSideLength = kwargs[ART_SIDE_LENGTH] if ART_SIDE_LENGTH in kwargs else None
		self.artOffsets = kwargs[ART_WINDOW_OFFSET] if ART_WINDOW_OFFSET in kwargs else None

		self._stopScraping = threading.Event()
		self._findWindowHandleAttempts = 0
		self.updateWindowHandle()

		if(callback):
			threading.Thread(target=self._scraper, args=(self.callback, self._stopScraping)).start()
		## Else let the user manually grab the information via properties

	## Getters

	def getSongDataDict(self):
		return {SONG:self.song, ARTIST:self.artist, ART:self.art}

	def getSongKey(self):
		return SONG

	def getArtistKey(self):
		return ARTIST

	def getArtKey(self):
		return ART

	## Properties

	@property
	def windowHandle(self):
		return self._windowHandle

	@windowHandle.setter
	def windowHandle(self, value):
		self._windowHandle = value

	@property
	def song(self):
		return self._song

	@song.setter
	def song(self, value):
		self._song = str(value)

	@property
	def artist(self):
		return self._artist

	@artist.setter
	def artist(self, value):
		self._artist = str(value)

	@property
	def art(self):
		return self._art

	@art.setter
	def art(self, value):
		self._art = value

	## Methods

	def stopScraping(self):
		self._stopScraping.set()


	def playSong(self):
		## Play the song
		keybd_event(0xB3, MapVirtualKey(0xB3, 0))
		## Restart the song
		keybd_event(0xB1, MapVirtualKey(0xB1, 0))


	def updateWindowHandle(self, callback=None):
		def getSpotifyWindowHandle(handle, extra):
			pid = GetWindowThreadProcessId(handle)[1]
			processName = psutil.Process(pid).name().lower()
			songMatch = SONG_DATA_RE.match(GetWindowText(handle))
			if(SPOTIFY in processName and songMatch):
				self.windowHandle = handle
				## Should really be a return False here to kill off the 
				## 	enumeration when a suitable handle is found, but that
				## 	produces a weird 'Things have gone VERY wrong' error.
				##	See: http://docs.activestate.com/activepython/3.1/pywin32/win32gui__EnumWindows_meth.html

		EnumWindows(getSpotifyWindowHandle, None)

		## Can't know which window will display the currently playing song
		## 	information unless it's playing music.
		try:
			if(not self.windowHandle):
				self._findWindowHandleAttempts += 1
				if(self._findWindowHandleAttempts > ATTEMPT_LIMIT):
					raise RuntimeError("No valid " + SPOTIFY + " windows available.")
				self.playSong()
				time.sleep(WAIT_TIME)	## Give Spotify a moment to start playing.
				self.updateWindowHandle()
		except RuntimeError as re:
			print(re, "Is it currently open and running?")
			self.stopScraping()

		if(callback):
			callback()


	def captureAlbumArt(self):
		while(self.windowHandle != GetForegroundWindow()):
			SetForegroundWindow(self.windowHandle)
			time.sleep(WAIT_TIME)	## Give Spotify a moment to come to the foreground
		ShowWindow(self.windowHandle, SW_SHOWMAXIMIZED)
		time.sleep(WAIT_TIME)	## Give Spotify a second to become maximized

		## Get the edges of the window
		left, top, right, bottom = GetWindowRect(self.windowHandle)
		left += self.artOffsets[0]
		bottom -= self.artOffsets[1]
		## Get the album art's location from those edges and user specified offsets.
		region = (left, bottom - self.artSideLength, left + self.artSideLength, bottom)
		return pyscreenshot.grab(bbox=region, childprocess=False)


	def updateSongData(self, callback=None):
		try:
			isNewSong = False
			windowText = GetWindowText(self.windowHandle)
			## Don't just endlessly loop if the window handle stops working
			##	(usually because the window was closed).
			if(not windowText):
				self.windowHandle = None
				raise RuntimeError("No valid " + SPOTIFY + " windows available.")
			songMatch = SONG_DATA_RE.match(windowText)
			if(songMatch):
				song = songMatch.group(1)
				artist = songMatch.group(2)
				## Check to make sure that the song data is for a new song.
				if(self.song != song or self.artist != artist):
					self.song = song
					self.artist = artist
					if(self.shouldGetArt):
						self.art = self.captureAlbumArt()

					## Callback only when the song has been updated.
					if(callback):
						try:
							callback(self.getSongDataDict())
						except TypeError as te:
							print("The callback function '" + callback.__name__ + "' should take at least 1 argument.", te)
							self.stopScraping()

		except RuntimeError as re:
			print(re, "Was it closed recently?")
			self.stopScraping()


	def _scraper(self, callback, stopScrapingEvent):
		while(not stopScrapingEvent.is_set()):
			self.updateSongData(callback)
			time.sleep(SHORT_WAIT)
