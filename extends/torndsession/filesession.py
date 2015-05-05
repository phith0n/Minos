#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright @ 2014 Mitchell Chu

import os
from os.path import join, exists, isdir
import datetime

from driver import SessionDriver
from extends.torndsession.session import SessionConfigurationError

utcnow = datetime.datetime.utcnow
try:
    import cPickle as pickle    # py2
except:
    import pickle               # py3

class FileSession(SessionDriver):
    """
    System File to save session object.
    """
    DEFAULT_SESSION_POSITION = './#_sessions' # default host is '#_sessions' directory which is in current directory.
    """
    Session file default save position.
    In a recommendation, you need give the host option.when host is missed, system will use this value by default.

    Additional @ Version: 1.1
    """

    def __init__(self, **settings):
        """
        Initialize File Session Driver.
        settings section 'host' is recommended, the option 'prefix' is an optional.
        if prefix is not given, 'default' is the default.
        host: where to save session object file, this is a directory path.
        prefix: session file name's prefix. session file like: prefix@session_id
        """
        super(FileSession, self).__init__(**settings)
        self.host = settings.get("host", self.DEFAULT_SESSION_POSITION)
        self._prefix = settings.get("prefix", 'default')
        if not exists(self.host):
            os.makedirs(self.host, 0700) # only owner can visit this session directory.
        if not isdir(self.host):
            raise SessionConfigurationError('session host not found')

    def get(self, session_id):
        session_file = join(self.host, self._prefix + session_id)
        if not exists(session_file): return {}

        rf = file(session_file, 'rb')
        session = pickle.load(rf)
        rf.close()
        now = utcnow()
        expires = session.get('__expires__', now)
        if expires >= now:
            return session
        return {}

    def save(self, session_id, session_data, expires=None):
        session_file = join(self.host, self._prefix + session_id)
        session_data = session_data if session_data else {}

        if not expires:
            session_data.update("__expires__", expires)
        wf = file(session_file, 'wb')
        pickle.dump(session_data, wf)
        wf.close()

    def clear(self, session_id):
        session_file = join(self.host, self._prefix + session_id)
        if exists(session_file):
            os.remove(session_file)

    def remove_expires(self):
        if not exists(self.host) or not isdir(self.host):return
        now = utcnow()
        for file in os.listdir(self.host):
            if file.startswith(self._prefix):
                session_file = join(self.host, file)
                f = open(session_file, 'rb')
                session = pickle.load(f)
                f.close()
                expires = session.get('__expires__', now)
                if expires <= now:
                    os.remove(session_file)
