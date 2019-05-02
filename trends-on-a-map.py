import urllib.request
import json
import tweepy
import folium
import time

# INSERT YOUR TWITTER API KEYS HERE
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
OAUTH_TOKEN = ''
OAUTH_TOKEN_SECRET = ''


def get_values(x):
    """strip all values of a string before the equal sign"""
    return x.split("=", 1)[-1]


def find_woeid(location):
    """
    this function finds the WOEID of a location.

    :param location: a location name as string
    :return: a list of WOID items with 'WOEID, Coordinates and Location name' (will return empty list if a location is not found)
    """
    woeids = []

    # replace spaces with + to prevent broken url
    location = location.replace(" ", "+")
    # build url, retrieve result and parse data to pull WOEID info
    with urllib.request.urlopen(
            "https://search.yahoo.com/sugg/gossip/gossip-gl-location/?appid=weather&output=sd1&p2=pt&command="
            + location) as url:
        result = json.loads(url.read().decode())
        result = result["r"]

        for data in result:
            woeid_info = data["d"].split("&")
            woeids.append(woeid_info)

    return woeids


def get_trendslist(woeid):
    """
    this function returns a list of trending tweets within a given WOEID location.

    :param woeid: a yahoo WOEID
    :return: returns a list of trending tweets within given WOIED
    """
    listoftweets = []

    # use tweepy to retrieve trending lists for given WOEID
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    api = tweepy.API(auth)
    trends = api.trends_place(woeid)
    for tweet in trends[0]["trends"]:
        # listoftweets.append(tweet["name"])
        listoftweets.append('<a href="' + tweet["url"] + '">' + tweet["name"] + '</a>')
    return listoftweets


def generate_map(locations, listoftrends):
    """
    this function generates a map with markers showing trending tweets.

    :param locations: a list of WOIED items as returned by the find_woeid() function
    :param listoftrends: a list of lists with trending tweets
    :return:
    """

    # create new map, set minimum zoom and stop infinite side scrolling
    map = folium.Map(min_zoom=3, no_wrap=True)
    trend_group = folium.FeatureGroup(name="Trending Tweet")

    #if locations is not an empty list, place markers into the trend_group layer with trending tweet info
    if locations:
        for a, b in zip(listoftrends, locations):
            #TODO figure out why second part of string with trend data does not show up.
            html = """Now Trending:  """ + "<br>".join(a[:40])
            iFrame = folium.IFrame(html=html, width=200, height=600)

            trend_group.add_child(folium.Marker(location=[float(get_values(b[3])), float(get_values(b[2]))],
                                                popup=folium.Popup(iFrame),
                                                icon=folium.Icon(color="red")))

    map.add_child(trend_group)
    map.add_child(folium.LayerControl())
    map.save(r"YOUR-FILEPATH\FILENAME.html")

# get location to search from user
user_input = input("Enter a location to find trending tweets: ")
user_locations = find_woeid(user_input)

nowtrending_lists = []
for location in user_locations:
    print(get_values(location[4]))
    # set repeat boolean to true
    repeat = True
    # while true make api request. if failed, wait 5 minutes then try again
    while repeat:
        try:
            nowtrending_lists.append(get_trendslist(get_values(location[1])))
            repeat = False
        except:
            print("TweepError. passing")
            break
    # wait 2 seconds before moving to next iteration
    time.sleep(2)

generate_map(user_locations, nowtrending_lists)
