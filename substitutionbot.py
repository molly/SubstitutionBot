# Copyright (c) 2014 Molly White
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
from secrets import *
from time import gmtime, strftime

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
offensive = re.compile(r"\b(deaths?|dead(ly)?|die(s|d)?|hurts?|"
                       r"(sex|child)[ -]?(abuse|trafficking)|"
                       r"injur(e|i?es|ed|y)|kill(ing|ed|er|s)?s?|"
                       r"wound(ing|ed|s)?|fatal(ly|ity)?|shoo?t(s|ing|er)?s?|"
                       r"crash(es|ed|ing)?|attack(s|ers?|ing|ed)?|"
                       r"murder(s|er|ed|ing)?s?|hostages?|rap(e|es|ed|ing)|"
                       r"assault(s|ed)?|pile-?ups?|massacre(s|d)?|"
                       r"assassinate(d|s)?|sla(y|in|yed|ys)|victims?|"
                       r"tortur(e|ed|ing|es)|execut(e|ion|ed)s?|"
                       r"gun(man|men|ned)|suicid(e|al|es)|bomb(s|ed)?|"
                       r"mass[- ]?graves?|bloodshed|state[- ]?of[- ]?emergency|"
                       r"al[- ]?Qaeda|blasts?|violen(t|ce))|lethal\W?\b",
                       flags=re.IGNORECASE)

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
    "trees": "stick towers"
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
            for item in results:
                headline = item["webTitle"]

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
    f.write("\n" + t + " " + headline)
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
