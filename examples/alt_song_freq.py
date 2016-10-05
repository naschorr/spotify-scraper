from time import sleep
from win32api import MapVirtualKey, keybd_event

from spotify_scraper import SpotifyScraper


## Looks at the randomness of Spotify's shuffle feature. 
## 	(Except, now the callback doesn't take any arguments.)
class AltSongFreq:
	def __init__(self, limit=1000, waitTime=1, **scraperArgs):
		self.songs = {}
		self.limit = limit
		self.waitTime = waitTime

		self.counter = 0
		self.scraper = SpotifyScraper(self.addSong, **scraperArgs)


	def dumpSongs(self):
		for key in sorted(self.songs, key=self.songs.get, reverse=True):
			print(key + ' = ' + str(self.songs[key]))


	def addSong(self):
		if(self.counter < self.limit):
			song = self.scraper.song + ' - ' + self.scraper.artist
			if(song in self.songs):
				self.songs[song] += 1
			else:
				self.songs[song] = 1
			self.counter += 1
			sleep(self.waitTime)
			self.nextSong()
		else:
			self.scraper.stopScraping()
			self.stopSong()
			self.dumpSongs()


	def nextSong(self):
		keybd_event(0xB0, MapVirtualKey(0xB0, 0))


	def stopSong(self):
		keybd_event(0xB2, MapVirtualKey(0xB2, 0))


def main():
	AltSongFreq(shouldGetArt=False)

main()