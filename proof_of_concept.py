#http://new.grtcbustracker.com/bustime/eta/getStopPredictionsETA.jsp
# agency=
# route=all
# &stop=2999
# import urequests as requests
import requests

result = requests.get(url="http://new.grtcbustracker.com/bustime/eta/getStopPredictionsETA.jsp"
    + "?agency="
    + "&route=all"
    + "&stop=2999"
)

xm = result.text.split("\n")
xml = [d for d in xm if len(d) > 1][1:-1]

print('\n'.join(xml))


inEntry = False
ArrivalStack = []
curMinute = 0 # pt
curRoute = "" # rn
curDirection = "" # fd
for line in xml:
    if "</pre>" in line:
        ArrivalStack.append([curMinute, curRoute, curDirection])
        continue
    if "<fd>" in line:
        curDirection = line.replace("<fd>", " ").replace("</fd>", " ").strip()
        continue
    if "<rn>" in line:
        curRoute = line.replace("<rn>", " ").replace("</rn>", " ").strip()
        continue
    if "<pt>" in line:
        curMinute = line.replace("<pt>", " ").replace("</pt>", " ").strip()
        continue

print(ArrivalStack)

# curl -X POST  \
#   --data-urlencode "agency=" \
#   --data-urlencode "route=all" \
#   --data-urlencode "stop=3626" \
