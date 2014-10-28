# coding=utf8
"""
admin.py - Willie Admin Module
Copyright 2010-2011, Michael Yanovich, Alek Rollyson, and Edward Powell
Copyright © 2012, Elad Alfassa <elad@fedoraproject.org>
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net/

"""
from __future__ import unicode_literals

import re
from willie import formatting
from willie.module import commands, priority, OP, HALFOP
from willie.tools import Nick


def default_mask(trigger):
    welcome = formatting.color('Welcome to:', formatting.colors.PURPLE)
    chan = formatting.color(trigger.sender, formatting.colors.TEAL)
    topic_ = formatting.bold('Topic:')
    topic_ = formatting.color('| ' + topic_, formatting.colors.PURPLE)
    arg = formatting.color('{}', formatting.colors.GREEN)
    return '{} {} {} {}'.format(welcome, chan, topic_, arg)


def setup(bot):
    #Having a db means pref's exists. Later, we can just use `if bot.db`.
    if bot.db and not bot.db.preferences.has_columns('topic_mask'):
        bot.db.preferences.add_columns(['topic_mask'])


@commands('op')
def op(bot, trigger):
    """
    Command to op users in a room. If no nick is given,
    willie will op the nick who sent the command
    """
    if bot.privileges[trigger.sender][trigger.nick] < OP:
        return
    if bot.privileges[trigger.sender][bot.nick] < OP:
        return bot.reply("I'm not a channel operator!")
    nick = trigger.group(2)
    channel = trigger.sender
    if not nick:
        nick = trigger.nick
    bot.write(['MODE', channel, "+o", nick])


@commands('deop')
def deop(bot, trigger):
    """
    Command to deop users in a room. If no nick is given,
    willie will deop the nick who sent the command
    """
    if bot.privileges[trigger.sender][trigger.nick] < OP:
        return
    if bot.privileges[trigger.sender][bot.nick] < OP:
        return bot.reply("I'm not a channel operator!")
    nick = trigger.group(2)
    channel = trigger.sender
    if not nick:
        nick = trigger.nick
    bot.write(['MODE', channel, "-o", nick])


@commands('voice')
def voice(bot, trigger):
    """
    Command to voice users in a room. If no nick is given,
    willie will voice the nick who sent the command
    """
    if bot.privileges[trigger.sender][trigger.nick] < OP:
        return
    if bot.privileges[trigger.sender][bot.nick] < HALFOP:
        return bot.reply("I'm not a channel operator!")
    nick = trigger.group(2)
    channel = trigger.sender
    if not nick:
        nick = trigger.nick
    bot.write(['MODE', channel, "+v", nick])


@commands('devoice')
def devoice(bot, trigger):
    """
    Command to devoice users in a room. If no nick is given,
    willie will devoice the nick who sent the command
    """
    if bot.privileges[trigger.sender][trigger.nick] < OP:
        return
    if bot.privileges[trigger.sender][bot.nick] < HALFOP:
        return bot.reply("I'm not a channel operator!")
    nick = trigger.group(2)
    channel = trigger.sender
    if not nick:
        nick = trigger.nick
    bot.write(['MODE', channel, "-v", nick])


@commands('kick')
@priority('high')
def kick(bot, trigger):
    """
    Kick a user from the channel.
    """
    if bot.privileges[trigger.sender][trigger.nick] < OP:
        return
    if bot.privileges[trigger.sender][bot.nick] < HALFOP:
        return bot.reply("I'm not a channel operator!")
    text = trigger.group().split()
    argc = len(text)
    if argc < 2:
        return
    opt = Nick(text[1])
    nick = opt
    channel = trigger.sender
    reasonidx = 2
    if not opt.is_nick():
        if argc < 3:
            return
        nick = text[2]
        channel = opt
        reasonidx = 3
    reason = ' '.join(text[reasonidx:])
    if nick != bot.config.nick:
        bot.write(['KICK', channel, nick, reason])


def configureHostMask(mask):
    if mask == '*!*@*':
        return mask
    if re.match('^[^.@!/]+$', mask) is not None:
        return '%s!*@*' % mask
    if re.match('^[^@!]+$', mask) is not None:
        return '*!*@%s' % mask

    m = re.match('^([^!@]+)@$', mask)
    if m is not None:
        return '*!%s@*' % m.group(1)

    m = re.match('^([^!@]+)@([^@!]+)$', mask)
    if m is not None:
        return '*!%s@%s' % (m.group(1), m.group(2))

    m = re.match('^([^!@]+)!(^[!@]+)@?$', mask)
    if m is not None:
        return '%s!%s@*' % (m.group(1), m.group(2))
    return ''


@commands('ban')
@priority('high')
def ban(bot, trigger):
    """
    This give admins the ability to ban a user.
    The bot must be a Channel Operator for this command to work.
    """
    if bot.privileges[trigger.sender][trigger.nick] < OP:
        return
    if bot.privileges[trigger.sender][bot.nick] < HALFOP:
        return bot.reply("I'm not a channel operator!")
    text = trigger.group().split()
    argc = len(text)
    if argc < 2:
        return
    opt = Nick(text[1])
    banmask = opt
    channel = trigger.sender
    if not opt.is_nick():
        if argc < 3:
            return
        channel = opt
        banmask = text[2]
    banmask = configureHostMask(banmask)
    if banmask == '':
        return
    bot.write(['MODE', channel, '+b', banmask])


@commands('unban')
def unban(bot, trigger):
    """
    This give admins the ability to unban a user.
    The bot must be a Channel Operator for this command to work.
    """
    if bot.privileges[trigger.sender][trigger.nick] < OP:
        return
    if bot.privileges[trigger.sender][bot.nick] < HALFOP:
        return bot.reply("I'm not a channel operator!")
    text = trigger.group().split()
    argc = len(text)
    if argc < 2:
        return
    opt = Nick(text[1])
    banmask = opt
    channel = trigger.sender
    if not opt.is_nick():
        if argc < 3:
            return
        channel = opt
        banmask = text[2]
    banmask = configureHostMask(banmask)
    if banmask == '':
        return
    bot.write(['MODE', channel, '-b', banmask])


@commands('quiet')
def quiet(bot, trigger):
    """
    This gives admins the ability to quiet a user.
    The bot must be a Channel Operator for this command to work.
    """
    if bot.privileges[trigger.sender][trigger.nick] < OP:
        return
    if bot.privileges[trigger.sender][bot.nick] < OP:
        return bot.reply("I'm not a channel operator!")
    text = trigger.group().split()
    argc = len(text)
    if argc < 2:
        return
    opt = Nick(text[1])
    quietmask = opt
    channel = trigger.sender
    if not opt.is_nick():
        if argc < 3:
            return
        quietmask = text[2]
        channel = opt
    quietmask = configureHostMask(quietmask)
    if quietmask == '':
        return
    bot.write(['MODE', channel, '+q', quietmask])


@commands('unquiet')
def unquiet(bot, trigger):
    """
    This gives admins the ability to unquiet a user.
    The bot must be a Channel Operator for this command to work.
    """
    if bot.privileges[trigger.sender][trigger.nick] < OP:
        return
    if bot.privileges[trigger.sender][bot.nick] < OP:
        return bot.reply("I'm not a channel operator!")
    text = trigger.group().split()
    argc = len(text)
    if argc < 2:
        return
    opt = Nick(text[1])
    quietmask = opt
    channel = trigger.sender
    if not opt.is_nick():
        if argc < 3:
            return
        quietmask = text[2]
        channel = opt
    quietmask = configureHostMask(quietmask)
    if quietmask == '':
        return
    bot.write(['MODE', opt, '-q', quietmask])


@commands('kickban', 'kb')
@priority('high')
def kickban(bot, trigger):
    """
    This gives admins the ability to kickban a user.
    The bot must be a Channel Operator for this command to work.
    .kickban [#chan] user1 user!*@* get out of here
    """
    if bot.privileges[trigger.sender][trigger.nick] < OP:
        return
    if bot.privileges[trigger.sender][bot.nick] < HALFOP:
        return bot.reply("I'm not a channel operator!")
    text = trigger.group().split()
    argc = len(text)
    if argc < 4:
        return
    opt = Nick(text[1])
    nick = opt
    mask = text[2]
    reasonidx = 3
    if not opt.is_nick():
        if argc < 5:
            return
        channel = opt
        nick = text[2]
        mask = text[3]
        reasonidx = 4
    reason = ' '.join(text[reasonidx:])
    mask = configureHostMask(mask)
    if mask == '':
        return
    bot.write(['MODE', channel, '+b', mask])
    bot.write(['KICK', channel, nick, ' :', reason])


@commands('topic')
def topic(bot, trigger):
    """
    This gives ops the ability to change the topic.
    The bot must be a Channel Operator for this command to work.
    """
    purple, green, bold = '\x0306', '\x0310', '\x02'
    if bot.privileges[trigger.sender][trigger.nick] < OP:
        return
    if bot.privileges[trigger.sender][bot.nick] < HALFOP:
        return bot.reply("I'm not a channel operator!")
    if not trigger.group(2):
        return
    channel = trigger.sender.lower()

    narg = 1
    mask = None
    if bot.db and channel in bot.db.preferences:
        mask = bot.db.preferences.get(channel, 'topic_mask')
    mask = mask or default_mask(trigger)
    mask = mask.replace('%s', '{}')
    narg = len(re.findall('{}', mask))

    top = trigger.group(2)
    args = []
    if top:
        args = top.split('~', narg)

    if len(args) != narg:
        message = "Not enough arguments. You gave {}, it requires {}.".format(
            len(args), narg)
        return bot.say(message)
    topic = mask.format(*args)

    bot.write(('TOPIC', channel + ' :' + topic))


@commands('tmask')
def set_mask(bot, trigger):
    """
    Set the mask to use for .topic in the current channel. {} is used to allow
    substituting in chunks of text.
    """
    if bot.privileges[trigger.sender][trigger.nick] < OP:
        return
    if not bot.db:
        bot.say("I'm afraid I can't do that.")
    else:
        bot.db.preferences.update(trigger.sender.lower(), {'topic_mask': trigger.group(2)})
        bot.say("Gotcha, " + trigger.nick)


@commands('showmask')
def show_mask(bot, trigger):
    """Show the topic mask for the current channel."""
    if bot.privileges[trigger.sender][trigger.nick] < OP:
        return
    if not bot.db:
        bot.say("I'm afraid I can't do that.")
    elif trigger.sender.lower() in bot.db.preferences:
        bot.say(bot.db.preferences.get(trigger.sender.lower(), 'topic_mask'))
    else:
        bot.say(default_mask(trigger))
