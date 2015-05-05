#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright @ 2014 Mitchell Chu

import datetime

from driver import SessionDriver
from extends.torndsession.session import SessionConfigurationError


class MemorySession(SessionDriver):
    '''
    save session data in process memory
    '''

    MAX_SESSION_OBJECTS = 1024
    """The max session objects save in memory.
    when session objects count large than this value,
    system will auto to clear the expired session data.
    """

    def __init__(self, **settings):
        # check settings
        super(MemorySession, self).__init__(**settings)
        host = settings.get("host")
        if not host:
            raise SessionConfigurationError('memory session driver can not found persistence position')
        if not hasattr(host, "session_container"):
            setattr(host, "session_container", {})
        self._data_handler = host.session_container
        # init some thing 

    def get(self, session_id):
        """
        get session object from host.
        """
        return self._data_handler.get(session_id)

    def save(self, session_id, session_data, expires=None):
        """
        save session data to host.
        if host's session objects is more then MAX_SESSION_OBJECTS
        system will auto to clear expired session data.
        after cleared, system will add current to session pool, however the pool is full.
        """
        session_data = session_data if session_data else {}
        session_data.update(__expires__=expires)
        if len(self._data_handler) >= self.MAX_SESSION_OBJECTS:
            self.remove_expires()
        if len(self._data_handler) >= self.MAX_SESSION_OBJECTS:
            print 'system session pool is full. need more memory to save session object.'
        self._data_handler[session_id]=session_data

    def clear(self, session_id):
        if self._data_handler.haskey(session_id):
            del self._data_handler[session_id]
    
    def remove_expires(self):
        for key, val in self._data_handler:
            now = datetime.datetime.utcnow()
            expires = val.get("__expires__", now)
            if now > expires:
                del self._data_handler[key]
