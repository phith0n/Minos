#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright @ 2014 Mitchell Chu
# 

from uuid import uuid4
import datetime

from extends.torndsession.driver import SessionDriverFactory

try:
    import cPickle as pickle #py2
except ImportError:
    import pickle #py3


class SessionManager(object):
    '''
    '''
    SESSION_ID = 'PYSESSID'
    DEFAULT_SESSION_LIFETIME = 3600 # seconds
    
    def __init__(self, handler):
        self._default_session_lifetime = datetime.datetime.utcnow() + datetime.timedelta(seconds = self.DEFAULT_SESSION_LIFETIME)
        self.handler = handler
        self.settings = {}       # session configurations
        self._expires = self._default_session_lifetime
        self._is_dirty = True
        self.__init_session_driver()
        self.__init_session_object() # 初始化Session对象

    def __init_session_object(self):
        session_id = self.handler.get_cookie(self.SESSION_ID)
        if not session_id:
            session_id = uuid4().hex
            self.handler.set_cookie(self.SESSION_ID,
                                    session_id,
                                    **self.__session_settings())
            self._is_dirty = True
            self.session = {}
        else:
            self.session = self.__get_session_object_from_driver(session_id)
            if not self.session:
                self.session = {}
                self._is_dirty = True
            else:
                self._is_dirty = False
        cookie_config = self.settings.get("cookie_config")
        if cookie_config:
            expires = cookie_config.get("expires")
            expires_days = cookie_config.get("expires_days")
            if expires_days is not None and not expires:
                expires = datetime.datetime.utcnow() + datetime.timedelta(days = expires_days)
            if expires and isinstance(expires, datetime.datetime):
                self._expires = expires
        self._expires = self._expires if self._expires else self._default_session_lifetime
        self._id = session_id

    def __init_session_driver(self):
        """
        setup session driver.
        """
        self.__init_settings()

        driver = self.settings.get("driver")
        if not driver: raise SessionConfigurationError('driver not found')
        driver_settings = self.settings.get("driver_settings", {})
        if not driver_settings: raise SessionConfigurationError('driver settings not found.')

        cache_driver = self.settings.get("cache_driver", True)
        if cache_driver:
            cache_name = '__cached_session_driver'
            cache_handler = self.handler.application
            if not hasattr(cache_handler, cache_name):
                setattr(cache_handler, cache_name, SessionDriverFactory.create_driver(driver, **driver_settings))
            session_driver = getattr(cache_handler, cache_name)
        else:
            session_driver = SessionDriverFactory.create_driver(driver, driver_settings)
        self.driver = session_driver(**driver_settings) # create session driver instance.

    def __get_session_driver(self):
        driver_name = self.setting.get("driver")
        cache_driver = self.settings.get("cache_driver", True)
        driver_settings = self.settings.get("driver_settings", {})
        if cache_driver:
            cache_name = '__cached_session_driver'
            if not hasattr( self.handler.application, cache_name):
                if not driver_name:raise SessionConfigurationError('driver missed')
                if not driver_settings: raise SessionConfigurationError('driver settings missed.')
                setattr( self.handler.application, cache_name, SessionDriverFactory.create_driver(driver_name, **driver_settings))
            driver = getattr(self.hanlder.application, cache_name)
        else:
            driver = SessionDriverFactory.create_driver(driver_name, **driver_settings)
        return driver

    def __init_settings(self):
        """
        Init session relative configurations.
        all configuration settings as follow:
        settings = dict(
            cookie_secret = "00a03c657e749caa89ef650a57b53ba(&#)(",
            debug = True,
            session = {
                driver = 'memory',
                driver_settings = {'host':self,}, # use application to save session data.
                force_persistence = True,
            cache_driver = True, # cache driver in application.
            cookie_config = {'expires_days':10, 'expires':datetime.datetime.utcnow(),}, # tornado cookies configuration
            },
        )
        driver:            default enum value: memory, file, redis, memcache.
        driver_settings:    the data driver need. settings may be the host, database, password, and so on.
                redis settings as follow:
                      driver_settings = {
                                    host = '127.0.0.1',
                              port = '6379',
                              db = 0, # where the session data to save.
                              password = 'session_db_password', # if database has password
                     }
        force_persistence:    default is False.
                In default, session's data exists in memory only, you must persistence it by manual.
                Generally, rewrite Tornado RequestHandler's prepare(self) and on_finish(self) to persist session data is recommended.
                         when this value set to True, session data will be force to persist everytime when it has any change.

        """
        session_settings = self.handler.settings.get("session")
        if not session_settings: # use default
            session_settings = {}
            session_settings.update(driver='memory', driver_settings={'host':self.handler.application}, force_persistence=True, cache_driver=True)
        driver = session_settings.get("driver")
        if not driver:
            raise SessionConfigurationError('driver is missed')
        self.settings = session_settings

    def __get_session_object_from_driver(self, session_id):
        """
        Get session data from driver.
        """
        return self.driver.get(session_id)

    def get(self, key, default=None):
        '''
        Return session value with name as key.
        '''
        self._is_dirty = True
        return self.session.get(key, default)

    def set(self, key, value):
        '''
        Add/Update session value
        '''
        self.session[key]=value
        self._is_dirty = True
        force_update = self.settings.get("force_persistence")
        if force_update:
            self.driver.save(self._id, self.session, self._expires)
            self._is_dirty = False

    def delete(self, key):
        '''
        Delete session key-value pair
        '''
        if self.session.has_key(key):
            del self.session[key]
            self._is_dirty = True
        force_update = self.settings.get("force_persistence")
        if force_update:
            self.driver.save(self._id, self.session, self._expires)
            self._is_dirty = False
    __deleteitem__ = delete

    def iterkeys(self):
        return iter(self.session)
    __iter__ = iterkeys

    def keys(self):
        '''
        Return all keys in session object
        '''
        return self.session.keys()

    def flush(self):
        """
        this method force system to do  session data persistence.
        """
        if self._is_dirty:
            self.driver.save(self._id, self.session, self._expires)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __getitem__(self, key):
        val = self.get(key)
        if val: return val
        raise KeyError('%s not found' % key) 

    def __contains__(self, key):
        '''
        '''
        return key in self.session

    @property
    def id(self):
        '''
        Return current session id
        '''
        if not hasattr(self, '_id'):
            self.__init_session_object()
        return self._id

    @property
    def expires(self):
        """
        The session object lifetime on server.
        this property could not be used to cookie expires setting.
        """
        if not hasattr(self, '_expires'):
            self.__init_session_object()
        return self._expires

    # def __generate_session_id(self):
    #     '''
    #     Generate unique session id by uuid4
    #     '''
    #     session_id = uuid4().hex
    #     self.handler.set_cookie(self.SESSION_ID,
    #                             session_id,
    #                             **self.__session_settings())
    #     return session_id

    def __session_settings(self):
        session_settings = self.settings.get('cookie_config', {})
        session_settings.setdefault('expires', None)
        session_settings.setdefault('expires_days', None)
        return session_settings

    # def __retrieve_current_session_id(self):
    #     session_id = self.handler.get_cookie(self.SESSION_ID)
    #     if session_id:return session_id
    #     return self.__generate_session_id()

class SessionMixin(object):
    '''
    '''
    
    @property
    def session(self):
        '''
        '''
        return self._create_mixin(self, '__session_manager', SessionManager)

    def _create_mixin(self, context, inner_property_name, session_handler):
        if not hasattr(context, inner_property_name):
            setattr(context, inner_property_name, session_handler(context))
        return getattr(context, inner_property_name)

class SessionConfigurationError(Exception):
    pass
