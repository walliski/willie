#coding: utf8
"""
__init__.py - Willie Init Module
Copyright 2008, Sean B. Palmer, inamidst.com
Copyright 2012, Edward Powell, http://embolalia.net
Copyright © 2012, Elad Alfassa <elad@fedoraproject.org>

Licensed under the Eiffel Forum License 2.

http://willie.dftba.net/
"""
from __future__ import unicode_literals
from __future__ import absolute_import

import sys
import os
import time
import threading
import traceback
import willie.bot as bot
import signal
import willie.web as web
from willie.tools import stderr

__version__ = '4.2.1'


def run(config):
    if config.core.delay is not None:
        delay = config.core.delay
    else:
        delay = 20
    # Inject ca_certs from config to web for SSL validation of web requests
    if hasattr(config, 'ca_certs') and config.ca_certs is not None:
        web.ca_certs  = config.ca_certs
    else:
        web.ca_certs = '/etc/pki/tls/certs/ca-bundle.crt'

    def signal_handler(sig, frame):
        if sig == signal.SIGUSR1 or sig == signal.SIGTERM:
            stderr('Got quit signal, shutting down.')
            p.quit('Closing')
    while True:
        try:
            p = bot.Willie(config)
            if hasattr(signal, 'SIGUSR1'):
                signal.signal(signal.SIGUSR1, signal_handler)
            if hasattr(signal, 'SIGTERM'):
                signal.signal(signal.SIGTERM, signal_handler)
            p.run(config.core.host, int(config.core.port))
        except KeyboardInterrupt:
            break
        except Exception as e:
            trace = traceback.format_exc()
            try:
                stderr(trace)
            except:
                pass
            logfile = open(os.path.join(config.logdir, 'exceptions.log'), 'a')
            logfile.write('Critical exception in core')
            logfile.write(trace)
            logfile.write('----------------------------------------\n\n')
            logfile.close()
            os.unlink(config.pid_file_path)
            os._exit(1)

        if not isinstance(delay, int):
            break
        if p.hasquit or config.exit_on_error:
            break
        stderr('Warning: Disconnected. Reconnecting in %s seconds...' % delay)
        time.sleep(delay)
    os.unlink(config.pid_file_path)
    os._exit(0)
