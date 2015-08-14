# -*- coding: utf-8 -*-
import Queue
import atexit
from modules import Gmail
from apscheduler.schedulers.background import BackgroundScheduler
from facebook import *
import str_formater
#import logging
#logging.basicConfig()


class Notifier(object):

    class NotificationClient(object):

        def __init__(self, gather, timestamp):
            self.gather = gather
            #self.logger = logger
            self.timestamp = timestamp
            #self.logger.debug("init notif client %s" % self.__class__.__name__)

        def run(self):
            self.timestamp = self.gather(self.timestamp)

    def __init__(self, profile, logger):
        self.logger = logger
        self.logger.debug("init notif %s" % self.__class__.__name__)
        self.q = Queue.Queue()
        self.profile = profile
        self.notifiers = [
            self.NotificationClient(self.handleEmailNotifications,    None),
            self.NotificationClient(self.handleFacebookNotifications, None),
        ]

        sched = BackgroundScheduler(timezone="UTC", daemon=True)
        sched.start()
        self.gather()
        sched.add_job(self.gather, 'interval', seconds=30*60)
        atexit.register(lambda: sched.shutdown(wait=False))

    def gather(self):
        [client.run() for client in self.notifiers]

    def handleEmailNotifications(self, lastDate):
        """Places new Gmail notifications in the Notifier's queue."""
        emails = Gmail.fetchUnreadEmails(self.profile, since=lastDate)
        if emails:
            lastDate = Gmail.getMostRecentDate(emails)

        def styleEmail(e):
            return "Nowy email od %s." % Gmail.getSender(e)

        for e in emails:
            self.q.put(styleEmail(e))

        return lastDate


    def handleFacebookNotifications(self, lastDate):
        oauth_access_token = self.profile['keys']['FB_TOKEN']

        graph = GraphAPI(oauth_access_token)
        results = []
        try:
            results = graph.request("me/notifications")
        except GraphAPIError:
            self.logger.error("error getting response form facebook api, for key: %s" % oauth_access_token, exc_info=True)
            return
        except:
            self.logger.error("error getting response form facebook api, for key: %s" % oauth_access_token, exc_info=True)

        if not len(results['data']) or not results.has_key('summary'):
            self.logger.debug("Brak nowych powiadomień na Fejsbuku: %s" % repr(results))
            return

        updates = []
        updated_time = results['summary']['updated_time']
        self.logger.debug(results['summary']['updated_time'])
        
        count = len(results['data'])
        if count == 1:
          self.q.put('Masz nowe powiadomienie z Facebooka')
        else:
          self.q.put('Masz nowe powiadomienia z Facebooka')

        for notification in results['data']:
            #str_formater.checkFormat(notification['title'], self.logger)
            title =  str_formater.unicodeToUTF8(notification['title'], self.logger)
            #updates.append(title)
            if updated_time > lastDate:
              self.q.put(title)
              self.logger.debug("from:" + repr(notification['from']) + " to:" +  repr(notification['to']) + " created_time:" + repr(notification['created_time']) + " unread:" +  repr(notification['unread']) )

        #count = len(results['data'])
        #mic.say("Masz " + str(count) + " nowych powiadomień na Fejsbuku.|" + "| ".join(updates) )
        return updated_time



    def getNotification(self):
        """Returns a notification. Note that this function is consuming."""
        try:
            notif = self.q.get(block=False)
            return notif
        except Queue.Empty:
            return None

    def getAllNotifications(self):
        """
            Return a list of notifications in chronological order.
            Note that this function is consuming, so consecutive calls
            will yield different results.
        """
        notifs = []

        notif = self.getNotification()
        while notif:
            self.logger.debug("got notification: %s" % notif)
            notifs.append(notif)
            notif = self.getNotification()

        return notifs
