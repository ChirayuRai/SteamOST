import urllib.request
import json
import os
import sys
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError
import subprocess
from spotipy.oauth2 import SpotifyClientCredentials
from pprint import pprint
from apiclient.discovery import build

def main():
    spotCode()

def spotCode():
    # initialize the environment
    os.environ["SPOTIPY_CLIENT_ID"] = 'ffb373cfd00543a49c1ce2c357a8e279'
    os.environ["SPOTIPY_CLIENT_SECRET"] = '02800250dd464bcbaa2e03bdaa68c5b9'
    os.environ["SPOTIPY_REDIRECT_URI"] = 'http://google.com/'

    # This is where the user puts in their Usernames
    # Be sure to use the proper_username file to make sure they are entering in the right usernames
    steamUsername = input("Enter your Steam64ID: ")
    spotifyUsername = input("Enter your Spotify Username: ")

    scope = 'playlist-modify-public'
    # Erase cache and prompt for user permission

    try:
        token = util.prompt_for_user_token(spotifyUsername, scope)
    except:
        os.remove(f".cache-{spotifyUsername}")
        token = util.prompt_for_user_token(spotifyUsername)

    # Create our spotifyObject
    spotifyObject = spotipy.Spotify(auth=token)

    # Gathering the Json data with all the user's games, imorted as a dictionary
    with urllib.request.urlopen("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=BD4740E2E03714FCCC19FB60BF56BDFB&steamid=" + str(steamUsername) + "&include_appinfo=true&format=json") as url:
        gameData = json.loads(url.read().decode())

    # The whole json data is a dictionary, with another dictionary inside it, with a
    # couple of lists inside it, with those lists containing dictionaries of info
    allGames = gameData['response']['games']
    listOfGames = []
    for i in range(0, len(allGames)):
        print('(' + str(i) + ') ' + allGames[i].get('name'))   # This prints the dictionary value for 'name' within the list
        listOfGames.append(allGames[i].get('name'))

    # use the list we created of the games in order to "select" which option you want
    # to choose for the OST stuff
    # Made an error handler to just check if the OST is on spotify or not
    findGame = input("Which game from your Steam library would you like to use? ")
    optionChosen = allGames[int(findGame)].get('name')

    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    searchOST = str(optionChosen) + " Soundtrack"
    searchForAlbum = spotify.search(q=searchOST, limit=1, type='album')

    try:
        fullAlbumID = searchForAlbum['albums']['items'][0]['uri'] #if the OST not found, there will be index error
        actualAlbumID = fullAlbumID[14:len(fullAlbumID)]
        webbrowser.open('https://open.spotify.com/album/' + str(actualAlbumID))
    except IndexError:
        youtubeCode(str(optionChosen))
        return

    # Goes through the OST and returns 5 track IDs, which will be used to create the recommended playlist
    tracks = spotify.album_tracks(fullAlbumID, limit=5, offset=0)
    trackList = []
    for i in range(0, 3):
        try:
            trackList.append(tracks['items'][i]['id'])
        except IndexError:
            if len(trackList) > 0 and len(trackList) < 6:
                break
            break

    # Creates the list of 20 similar tracks and adds them to the new playlist
    recs = spotify.recommendations(seed_tracks=trackList)

    createPlaylist = spotifyObject.user_playlist_create(user=spotifyUsername,name="Songs similar to " + str(optionChosen), public=True, description="A recommended playlist based off of " + str(optionChosen))
    usersPlaylists = spotifyObject.user_playlists(user=spotifyUsername)
    createdPlaylistID = usersPlaylists['items'][0]['id']
    listOfRecs = []
    for i in range(0, 20):
        listOfRecs.append(recs['tracks'][i]['id'])

    for i in range(0, 1):
        spotifyObject.user_playlist_add_tracks(user=spotifyUsername, playlist_id=createdPlaylistID, tracks=listOfRecs, position=None)
    print("The playlist should now be generated :D")

def youtubeCode(chosen):
    # Takes the game name and then searches up OST along with it. Returns the first search result.
    api_key = "AIzaSyBDKRAarw5MkceCM1LXpeyVuB_0_9-8JDY"
    youtube = build(serviceName='youtube', version='v3', developerKey=api_key)
    req = youtube.search().list(q=str(chosen) + " OST", part='snippet', type='video', maxResults='1')
    res = req.execute()
    OstVidId = res['items'][0]['id']['videoId']
    webbrowser.open("https://www.youtube.com/watch?v=" + str(OstVidId))

if __name__ == "__main__":
    main()
