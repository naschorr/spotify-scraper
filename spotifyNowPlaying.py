import mutagen
import pyaudio
import time
import pyscreenshot
from PIL import Image
import psutil
import re
from win32con import SW_SHOWMAXIMIZED
from win32gui import GetWindowText, EnumWindows, SetForegroundWindow, GetForegroundWindow, ShowWindow, GetWindowRect
from win32process import GetWindowThreadProcessId
from win32api import MapVirtualKey, keybd_event

## Configs
INIT_ATTEMPTS = 5
WAIT_TIME = 1
SONG_RE_COMPILED = re.compile(r'(.+) - (.+)')

## String literals
SPOTIFY = "spotify"
EMPTY_STR = ""

## Define capture regions and offsets
ALBUM_ART_SIZE = 400			# 400px^2
ALBUM_ART_OFFSET = (8, 119)		# (Offset from left side of window, Offset from bottom of window)

## Globals
spotifyWindowHandle = None
currentSong = None
currentArtist = None


def initSpotifyData(handle, callback=None):
	global spotifyWindowHandle
	global currentSong
	global currentArtist

	pid = GetWindowThreadProcessId(handle)[1]
	try:
		process = psutil.Process(pid)
		pName = process.name().lower()
		songMatch = SONG_RE_COMPILED.match(GetWindowText(handle))
		if(SPOTIFY in pName and songMatch):
			spotifyWindowHandle = handle
			currentSong = songMatch.group(1)
			currentArtist = songMatch.group(2)

			if(callback):
				callback()
	except psutil.AccessDenied as error:
		print("Access Denied", error)


def updateSpotifyData(callback=None):
	global currentSong
	global currentArtist

	if(not spotifyWindowHandle):
		print("Can't update without a window handle")
		return

	songMatch = SONG_RE_COMPILED.match(GetWindowText(spotifyWindowHandle))
	if(songMatch):
		song = songMatch.group(1)
		artist = songMatch.group(2)
		if(currentSong != song or currentArtist != artist):
			currentSong = songMatch.group(1)
			currentArtist = songMatch.group(2)

			if(callback):
				callback()


def moveSpotifyToForeground():
	if(spotifyWindowHandle):
		ShowWindow(spotifyWindowHandle, SW_SHOWMAXIMIZED)
		SetForegroundWindow(spotifyWindowHandle)
	else:
		print("Can't move to foreground without a handle")


def isSpotifyInForeground():
	if(spotifyWindowHandle):
		if(spotifyWindowHandle == GetForegroundWindow()):
			return True
		else:
			return False
	else:
		print("Can't check if it's in the foreground without a handle")


def captureRegion(region):
	moveSpotifyToForeground()
	if(isSpotifyInForeground()):
		return pyscreenshot.grab(bbox=region, childprocess=False)
	else:
		time.sleep(WAIT_TIME)
		return captureRegion(region)


def getAlbumArt():
	left, top, right, bottom = GetWindowRect(spotifyWindowHandle)
	left += ALBUM_ART_OFFSET[0]
	bottom -= ALBUM_ART_OFFSET[1]
	return captureRegion((left, bottom - ALBUM_ART_SIZE, left + ALBUM_ART_SIZE, bottom))


def playMedia():
	## Restart the song
	keybd_event(0xB1, MapVirtualKey(0xB1, 0))
	## Play the song
	keybd_event(0xB3, MapVirtualKey(0xB3, 0))


def init(callback=None):
	initAttemptCtr = 0
	while(not spotifyWindowHandle):
		## Spotify doesn't put the song/artist info in the window text unless the song is playing.
		if(initAttemptCtr > INIT_ATTEMPTS):
			playMedia()
			initAttemptCtr = 0
		EnumWindows(initSpotifyData, callback)
		initAttemptCtr += 1
		time.sleep(WAIT_TIME)


def buildSong():
	print(currentSong + ' - ' + currentArtist)
	getAlbumArt().show()


def main():
	init(buildSong)

	while(True):
		updateSpotifyData(buildSong)


if __name__ == '__main__':
	main()