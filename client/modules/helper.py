# -*- coding: utf-8 -*-
#import str_formater
import re

WORDS = ["POMOC", "POMOCY"]

class X:
  HELP  = {"name": "xbmc",
           "description": "XBMC służy do sterowania odtwarzeniem muzyki, filmów, seriali oraz zdjęć.",
           "samples": ["zagraj zespół kult", "odtwazaj film gwiezdne wojny", "włacz radio ram"],
           "topics": {"muzyka": "powiedz odtwarzaj lub gra lub zagraj lub puść,|"+
                                 "następnie zespół lub zespołu lub artystę lub wykonawcę lub płyty,|" +
                                 "a następnie właściwą nazwę wykonawcy.|"+
                                 "Kommenda ta, doda do kolejki odtwarzania wszystkie albumy wykonawcy.",
                       "film":   "powiedz odtwarzaj lub graj lub zagraj lub puść,| "+
                                 "następnie film, " +
                                 "a następnie polski tytuł filmu.|"+
                                 "Jeżeli wyszukiwanie zwróci więcej niż jeden wynik,|"+
                                 "to wszystkie filmy zostaną dodane do kolejki.|"+
                                 "Nie trzeba wypowiadać pełnej nazwy filmu,| "+
                                 "wystarczy użyć unikalnego słowa lub frazy",
                      "uwagi ogólne": "jeżeli nie udaje się prawidłowo rozpoznać nazwy artysty lub filmu,|"+
                                      "nazwę można przeliterować."
                      }
          }

class Y:
  HELP  = {"name": "pogoda",
           "description": "Możesz poznać lokalną prognozę pogody na dziś, jutro lub pojutrze",
           "samples": ["jaka jest prognoza pogody", "jaka będzie pogoda jutro", "prognoza na wtorek"],

           # "topics": {"muzyka": "powiedz odtwarzaj lub gra lub zagraj lub puść| "+
           #                       "następnie zespół lub zespołu lub artystę lub wykonawcę lub płyty|" +
           #                       "a następnie właściwą nazwę wykonawcy.|"+
           #                       "Kommenda ta, doda do kolejki odtwarzania wszystkie albumy wykonawcy.",
           #             "film":   "powiedz odtwarzaj lub graj lub zagraj lub puść| "+
           #                       "następnie film" +
           #                       "a następnie polski tytuł filmu.|"+
           #                       "Jeżeli wynik wyszukania zwróci więcej niż jeden wynik,"+
           #                       "to wszystkie filmy zostaną dodane do kolejki.|"+
           #                       "Nie trzeba wypowiadać pełnej nazwy filmu,|"+
           #                       "wystarczy użyć unikalnego słowa lub frazy",
           #            "uwagi ogólne": "jeżeli nie udaje się prawidłowo rozpoznać nazwy artysty lub filmu|"+
           #                            "nazwę można przeliterować."
           #            }
          }

class Mic:
    def say(self, msg):
        print "say:", msg

    def activeListen(self):
        input = raw_input("YOU: ")
        #input = str_formater.unicodeToUTF8(input, self.logger)
        if isinstance(input, unicode):
            input = input.encode('utf-8')

        return input

def handle(text, mic, profile, logger, modules):
    """
        Reads help messages to all modules

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
    """

    mic.say("Witaj w interaktywnym samouczku.")

    helps = {}
    for module in modules:
        if hasattr(module, 'HELP'):
            h = module.HELP
            helps[h["name"]] = h

    org_subject = ""
    words = text.split(" ")
    if len(words) > 1 and "pomoc" in words[0]:
        if words[1] in helps:
            org_subject = words[1]

    repeat = True
    while repeat:
        if org_subject:
            subject = org_subject
            repeat  = False
        else:
            mic.say("Aby wysłuchać szczegółowych wyjaśnień podaj nazwę interesującego Cię tematu.")
            mic.say("Powiedz wszystkie tematy aby poznać listę wszystkich tematów.")
            mic.say("Aby przerwać powiedz zakończ.")
            subject = mic.activeListen()

        if subject == "zakończ":
            mic.say("Kończę interaktywny samouczek.")
            #repeat = False
            break

        if subject == "wszystkie tematy":
            for h in sorted(helps.keys()):
                mic.say(h)

        elif subject in helps:
            help = helps[subject]
            mic.say("Temat: " + help["name"])
            mic.say(help["description"])

            if help.has_key("samples"):
                mic.say("Przykłady poleceń")
                for s in help["samples"]:
                    mic.say(s)

            if help.has_key("topics"):
                mic.say("Aby wysłuchać wyjaśnień na temat konkretnego podtematu wybierz jedną z opcji.")
                repeat_topic = True
                while repeat_topic:
                    #mic.say("Podtematy: ")
                    for t in sorted(help["topics"].keys()):
                        mic.say(t)
                    mic.say("By przerwać powiedz zakończ.")
                    topic = mic.activeListen()

                    if topic == "zakończ":
                        break

                    if topic in help["topics"]:
                        mic.say(help["topics"][topic])
                        mic.say("Podtematy")
                    else:
                        mic.say("Wybacz, ale nie ma takiego podtematu w samouczku.")
        else:
            mic.say("Wybacz, ale nie ma takiego tematu w samouczku.")

def isValid(text):
    """
        Returns True if the input is related to module contextual help.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\bpomoc(y)?\b', text, re.IGNORECASE))


if __name__ == "__main__":

    m = Mic()
    x = X()
    y = Y()
    t = "pomoc xbmc"
    print isValid(t)
    handle(t, m, None, None, [x, y])
