# Copyright (c) 2014–2015 Molly White
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import re
import HTMLParser
import json
import tweepy
import urllib2
from offensive import offensive
from secrets import *
from time import gmtime, strftime

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

substitutions = {
    "witnesses": "these dudes I know",
    "witness": "this dude I know",
    "allegedly": "kinda probably",
    "alleged": "kinda probably",
    "new study": "Tumblr post",
    "new studies": "Tumblr posts",
    "rebuild": "avenge",
    "rebuilds": "avenges",
    "rebuilding": "avenging",
    "space": "spaaace",
    "google glass": "Virtual Boy",
    "google glasses": "Virtual Boys",
    "smartphone": "Pokedex",
    "phone": "Pokedex",
    "cellphone": "Pokedex",
    "smartphones": "Pokedexes",
    "cellphones": "Pokedex",
    "phones": "Pokedex",
    "electric": "atomic",
    "electrical": "atomic",
    "electronic": "atomic",
    "senator": "Elf-Lord",
    "senators": "Elf-Lords",
    "car": "cat",
    "cars": "cats",
    "election": "eating contest",
    "elections": "eating contest",
    "congressional leaders": "river spirits",
    "congressional leader": "river spirit",
    "homeland security": "Homestar Runner",
    "could not be reached for comment": "is guilty and everyone knows it",
    "ice": "floor water",
    "glove": "hand-coat",
    "gloves": "hand-coats",
    "sun": "spacelight",
    "bird": "flappy plane",
    "birds": "flappy planes",
    "tweet": "beep",
    "tweets": "beeps",
    "tweeting": "beeping",
    "tree": "stick tower",
    "trees": "stick towers",
    "basketball": "shootyhoops",
    "NBA": "shootyhoops",
    "gun": "point-and-shooty",
    "guns": "point-and-shooties",
    "automatic weapon": "automatic liberty machine",
    "automatic weapons": "automatic liberty machines",
    "automatic rifle": "automatic liberty machine",
    "automatic rifles": "automatic liberty machines",
    "semi-automatic weapon": "taste of liberty",
    "semi-automatic weapons": "tastes of liberty",
    "Ron Paul": "Uncle Liberty",
    "Rand Paul": "Cousin Liberty",
    "robot": "smashy-mashy walk-and-crashy",
    "robots": "smashy-mashy walk-and-crashies",
    "force": "horse",
    "forces": "horses"
}

hparser = HTMLParser.HTMLParser()


def get():
    # Get the headlines, iterate through them to try to find a suitable one
    page = 1
    while page <= 3:
        try:
            request = urllib2.Request(
                "http://content.guardianapis.com/search?format=json&page-size=50&page=" +
                str(page) + "&api-key=" + GUARDIAN_KEY)
            response = urllib2.urlopen(request)
        except urllib2.URLError as e:
            print e.reason
        else:
            blob = json.load(response)
            results = blob["response"]["results"]
            results = results
            for item in results:
                headline = item["webTitle"].encode('utf-8', 'ignore')

                # Skip anything too offensive
                if not tact(headline):
                    continue

                # Remove attribution string
                if "|" in headline:
                    headline = headline.split("|")[:-1]
                    headline = ' '.join(headline).strip()

                if process(headline.split()):
                    return
                else:
                    page += 1

    # Log that no tweet could be made
    f = open(os.path.join(__location__, "substitutionbot.log"), 'a')
    t = strftime("%d %b %Y %H:%M:%S", gmtime())
    f.write("\n" + t + " No possible tweet.")
    f.close()


def process(headline):
    # Do the substitution
    replacement = False
    for key in substitutions.keys():
        for index, word in enumerate(headline):
            if word.lower() == key:
                headline[index] = substitutions[key]
                replacement = True
    if not replacement:
        return False

    headline = " ".join(headline)
    headline = hparser.unescape(headline)

    # Don't tweet anything that's too long
    if len(headline) > 140:
        return False

    # Don't tweet a headline we've tweeted before
    f = open(os.path.join(__location__, "substitutionbot.log"), 'r')
    log = f.read()
    f.close()
    if headline in log:
        return False

    # All systems go!
    return tweet(headline)


def tweet(headline):
    # Actually Tweet this thing!
    auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
    auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)
    api = tweepy.API(auth)
    tweets = api.user_timeline('CyberPrefixer')

    # Log tweet to file
    f = open(os.path.join(__location__, "substitutionbot.log"), 'a')
    t = strftime("%d %b %Y %H:%M:%S", gmtime())
    f.write("\n" + t + " " + headline.encode('utf-8', 'replace'))
    f.close()

    # Post tweet
    api.update_status(headline)
    return True


def tact(headline):
    # Avoid producing particularly tactless tweets
    if re.search(offensive, headline) is None:
        return True
    else:
        return False

if __name__ == "__main__":
    get()
