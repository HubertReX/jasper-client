import math
import audioop
import random
import struct

THRESHOLD_MULTIPLIER = 1.8
RATE = 160
CHUNK = 10
THRESHOLD_TIME = 1
LISTEN_TIME = 10
LISTEN_TIME = 10

def get_chunk(chunk):
  res = []
  for a in range(chunk):
    #data = random.randint(1, 16)
    data = 16 + int(16 * math.sin( math.radians( a*36))) + random.randint(1, 6)
    #print data
    res.append(data)
  print res
  res = struct.pack('i'*len(res), *res)
  
  return res

def getScore(data):
    rms = audioop.rms(data, 2)
    score = rms / 3
    print "score:", score, " rms:", rms
    return score

print "samples:", RATE / CHUNK * THRESHOLD_TIME

lastN = [15 for i in range(30)]
print lastN
average = sum(lastN) / len(lastN)
print "average: ", average

for i in range(0, RATE / CHUNK * THRESHOLD_TIME):
  data = get_chunk(CHUNK)
  lastN.pop(0)
  lastN.append(getScore(data))
  print lastN
  average = sum(lastN) / len(lastN)
  print "average: ", average, " sum:", sum(lastN), " len:", len(lastN)


THRESHOLD = average * THRESHOLD_MULTIPLIER
print "THRESHOLD: ", THRESHOLD 