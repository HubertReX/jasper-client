# -*- coding: utf-8 -*-
import feedparser
import app_utils
import re
from semantic.numbers import NumberService

WORDS = ["WIADOMOŚCI", "AKTUALNOŚCI", "INFORMACJE"]
HELP  = {"name": "wiadomości",
         "description": "Dzięki temu poleceniu możesz poznać akutalne wiadomości.| Możesz również wysłanie wybranych informacji mailem.",
         "samples": ["podaj aktualne wiadomości", "przeczytaj mi aktualności", "masz jakieś nowe informacje?"],
         "topics": {"wysyłka":  "Po przeczytaniu nagłówków wiadomości możesz poprosić o ich wysłanie na maila.| "+
                                "Powiedz tak lub poproszę aby otrzymać wszystkie wiadomości.|"+
                                "Powiedz pierwszy, pierwszą lub pierwsza aby dostać jedynie pierwszy artykuł."
                    }
          }


PRIORITY = 3

URL = 'http://news.ycombinator.com'


class Article:

    def __init__(self, title, URL):
        self.title = title
        self.URL = URL


def getTopArticles(maxResults=None):
    d = feedparser.parse("https://news.google.com/news/feeds?pz=1&cf=all&ned=pl_pl&hl=pl&output=rss")

    count = 0
    articles = []
    for item in d['items']:
        articles.append(Article(item['title'], item['link'].split("&url=")[1]))
        count += 1
        if maxResults and count > maxResults:
            break

    return articles


def handle(text, mic, profile, logger, modules):
    """
        Responds to user-input, typically speech text, with a summary of
        the day's top news headlines, sending them to the user over email
        if desired.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
    """
    mic.say("Proszę o cierpliwość, pobieram aktualne wiadomości.")
    articles = getTopArticles(maxResults=3)
    titles = [" ".join(x.title.split(" - ")[:-1]) for x in articles]
    all_titles = "| ".join(str(idx + 1) + ") " +
                             title for idx, title in enumerate(titles))

    def handleResponse(text):

        def extractOrdinals(text):
            output = []
            if 'pierwszy' in text or 'pierwsza' in text or 'pierwszą' in text:
                output.append(1)
            if 'drugi' in text or 'druga' in text or 'drugą' in text:
                output.append(2)
            if 'trzeci' in text or 'trzecia' in text or 'trzecią' in text:
                output.append(3)
            if 'czwarty' in text or 'czwarta' in text or 'czwartą' in text:
                output.append(4)
            if 'piąty' in text or 'piąta' in text or 'piątą' in text:
                output.append(5)

            return output
            #output = []
            #service = NumberService()
            #if text:
            #  for w in text.split():
            #      if w in service.__ordinals__:
            #          output.append(service.__ordinals__[w])
            #return [service.parse(w) for w in output]

        chosen_articles = extractOrdinals(text)
        send_all = not chosen_articles and app_utils.isPositive(text)

        if send_all or chosen_articles:
            mic.say("Już się robi, proszę o jedną chwilę")

            if profile['prefers_email']:
                body = "<ul>"

            def formatArticle(article):
                tiny_url = app_utils.generateTinyURL(article.URL)

                if profile['prefers_email']:
                    return "<li><a href=\'%s\'>%s</a></li>" % (tiny_url,
                                                               article.title)
                else:
                    return article.title + " -- " + tiny_url

            for idx, article in enumerate(articles):
                if send_all or (idx + 1) in chosen_articles:
                    article_link = formatArticle(article)

                    if profile['prefers_email']:
                        body += article_link
                    else:
                        if not app_utils.emailUser(profile, logger, SUBJECT="", BODY=article_link):
                            mic.say(
                                "Wybacz, ale mam problem z wysłaniem wiadomości.| Sprawdź proszę podany numer telefonu i operatora.")
                            return

            # if prefers email, we send once, at the end
            if profile['prefers_email']:
                body += "</ul>"
                if not app_utils.emailUser(profile, logger, SUBJECT="Twoje wiadomości", BODY=body):
                    mic.say(
                        "Wybacz, ale mam problem z wysłaniem wiadomości.| Sprawdź proszę podany numer telefonu i operatora.")
                    return

            mic.say("Gotowe")

        else:

            mic.say("W porządku, nie wysyłam wiadomości")

    if 'phone_number' in profile:
        mic.say("Oto najważniejsze wiadomości.| " + all_titles.encode('utf-8') +
                ".| Czy mam wysłać Ci wiadomości? Którąś konkretnie?")
        handleResponse(mic.activeListen())

    else:
        mic.say(
            "Oto najważniejsze wiadomości.| " + all_titles)


def isValid(text):
    """
        Returns True if the input is related to the news.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\b(wiadomości|aktualności|informacje)\b', text, re.IGNORECASE))
