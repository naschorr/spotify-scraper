import sys
import os.path

## This just adds the root directory to Python's PATH variable. It isn't
## necessary for normal operation.
sys.path.append(os.path.sep.join(os.path.realpath(__file__).split(os.path.sep)[:-2]))

from spotify_scraper import SpotifyScraper

def printSong(songDict):
	print(songDict["artist"], '-', songDict["song"])

scraper = SpotifyScraper(printSong, shouldGetArt=False)
