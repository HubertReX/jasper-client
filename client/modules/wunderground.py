import requests

if __name__ == "__main__":
  #r = requests.get("http://api.wunderground.com/api/df25024c48577110/forecast/lang:PL/q/Poland/Wroclaw.json")
  r = requests.get("http://api.wunderground.com/api/df25024c48577110/forecast10day/lang:PL/q/Poland/Wroclaw.json")
  data = r.json()

  #print data
  for day in data['forecast']['simpleforecast']['forecastday']:
      for el in day.keys():
        print "  %s %s" % (el, day[el])
      #print day['date']['weekday'] + ":"
      #print "Conditions: ", day['conditions']
      #print "High: ", day['high']['celsius'] + "C", "Low: ", day['low']['celsius'] + "C", '\n'
