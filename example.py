from spotify_scraper import SpotifyScraper

def printSong(songDict):
	print(songDict["artist"], '-', songDict["song"])

scraper = SpotifyScraper(printSong, shouldGetArt=False)