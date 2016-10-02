from time import sleep
from win32api import MapVirtualKey, keybd_event

from spotify_scraper import SpotifyScraper


class SongFreq:
	def __init__(self, waitTime=1, limit=1000):
		self.songs = {}
		self.scraper = None
		self.waitTime = waitTime
		self.limit = limit
		self.counter = 0


	@property
	def scraper(self):
		return self._scraper


	@scraper.setter
	def scraper(self, value):
		self._scraper = value


	def dumpSongs(self):
		for key in sorted(self.songs, key=self.songs.get, reverse=True):
			print(key + ' = ' + str(self.songs[key]))


	def addSong(self, songDict):
		if(self.counter <= self.limit):
			song = songDict["artist"] + ' - ' + songDict["song"]
			if(song in self.songs):
				self.songs[song] += 1
			else:
				self.songs[song] = 1
			self.counter += 1
			sleep(self.waitTime)
			self.nextSong()
		else:
			if(self.scraper):
				self.scraper.stopScraping()
			self.dumpSongs()
			self.stopSong()


	def nextSong(self):
		keybd_event(0xB0, MapVirtualKey(0xB0, 0))


	def stopSong(self):
		keybd_event(0xB2, MapVirtualKey(0xB2, 0))


songFreq = SongFreq()
scraper = SpotifyScraper(songFreq.addSong, shouldGetArt=False)
songFreq.scraper = scraper