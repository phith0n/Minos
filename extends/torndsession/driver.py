#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright @ 2014 Mitchell Chu

class SessionDriver(object):
    '''
    abstact class for all real session driver implements.
    '''
    def __init__(self, **settings):
        self.settings = settings

    def get(self, session_id):
        raise NotImplementedError()

    def save(self, session_id, session_data, expires=None):
        raise NotImplementedError()

    def clear(self, session_id):
        raise NotImplementedError()

    def remove_expires(self):
        raise NotImplementedError()

class SessionDriverFactory(object):
    '''
    session driver factory
    use input settings to return suitable driver's instance
    '''
    @staticmethod
    def create_driver(driver, **setings):
        module_name = 'extends.torndsession.%ssession' % driver.lower()
        module = __import__(module_name, globals(), locals(), ['object'], -1)
        # must use this form.
        # use __import__('torndsession.' + driver.lower()) just load torndsession.__init__.pyc
        cls = getattr(module, '%sSession' % driver.capitalize())
        if not 'SessionDriver' in [base.__name__ for base in cls.__bases__]:
            raise InvalidSessionDriverException('%s not found in current driver implements ' % driver)
        return cls              # just return driver class. 

class InvalidSessionDriverException(Exception):
    pass
