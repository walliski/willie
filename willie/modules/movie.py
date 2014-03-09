# -*- coding: utf8 -*-
"""
imdb.py - Willie Movie Information Module
Copyright © 2012-2013, Elad Alfassa, <elad@fedoraproject.org>
Licensed under the Eiffel Forum License 2.

This module relies on imdbapi.com
"""
import json
import willie.web as web
import willie.module


@willie.module.commands('movie', 'imdb')
@willie.module.example('.movie Movie Title')
def movie(bot, trigger):
    """
    Returns some information about a movie, like Title, Year, Rating, Genre and IMDB Link.
    """
    if not trigger.group(2):
        return
    word = trigger.group(2).rstrip()
    uri = "http://www.imdbapi.com/?t=" + word
    u = web.get(uri, 30)
    data = json.loads(u.decode('utf-8'))  # data is a Dict containing all the information we need
    if data['Response'] == 'False':
        if 'Error' in data:
            message = '[MOVIE] %s' % data['Error']
        else:
            bot.debug(__file__, 'Got an error from the imdb api, search phrase was %s' % word, 'warning')
            bot.debug(__file__, str(data), 'warning')
            message = '[MOVIE] Got an error from imdbapi'
    else:
        message = '[MOVIE] Title: ' + data['Title'] + \
                  ' | Year: ' + data['Year'] + \
                  ' | Rating: ' + data['imdbRating'] + \
                  ' | Genre: ' + data['Genre'] + \
                  ' | IMDB Link: http://imdb.com/title/' + data['imdbID']
    bot.say(message)
