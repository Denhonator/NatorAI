import urllib.request
import json

channelIdUrl = "https://api.twitch.tv/kraken/users?login=denhonator"
headers2={
'Client-ID': 'lxnmq2fya9fq511vh3d2dbcmasqgra',
'Accept': 'application/vnd.twitchtv.v5+json',
'Content-Type': 'application/json'
}
req2 = urllib.request.Request(channelIdUrl, None, headers2, None, False, 'GET')
resp2 = urllib.request.urlopen(req2)
print(resp2.read())

url = 'https://api.twitch.tv/kraken/channels/47999987/follows'
headers = {b'Accept': bytes('application/vnd.twitchtv.v5+json', encoding='utf-8'),
           b'Client-ID': bytes('lxnmq2fya9fq511vh3d2dbcmasqgra', encoding='utf-8'),
           b'Authorization': bytes('OAuth j4qiq2a6llnpz02lkw8r5hmqf16gfn', encoding='utf-8'),
           b'Content-Type': bytes('application/json', encoding='utf-8')
           }
req = urllib.request.Request(url, None, headers, None, False, 'GET')
try:
    resp = urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    print(e.code)
    print(e.reason)
    print(e.headers)

#data = resp.read()

#url2 += '&scope=channel_subscriptions'
#url2 += '&access_token=j4qiq2a6llnpz02lkw8r5hmqf16gfn'

#req = urllib.request.Request(url)
#resp = urllib.request.urlopen(req)
#data = resp.read()
#http://localhost/#access_token=j4qiq2a6llnpz02lkw8r5hmqf16gfn&id_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjEifQ.eyJhdWQiOiJseG5tcTJmeWE5ZnE1MTF2aDNkMmRiY21hc3FncmEiLCJleHAiOjE1MjU1NTE0MzAsImlhdCI6MTUyNTU1MDUzMCwiaXNzIjoiaHR0cHM6Ly9pZC50d2l0Y2gudHYvb2F1dGgyIiwic3ViIjoiNDc5OTk5ODciLCJhenAiOiJseG5tcTJmeWE5ZnE1MTF2aDNkMmRiY21hc3FncmEiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJEZW5ob25hdG9yIn0.Dr8aOFbBaVWkgfo55ZM8JDYeeVZCsJcHc8hFL6Ztbv9t1lKZ3YYCjNNwsSki2r_EAUrGP7xkcoqdKvZdDz8GefWjg2UPSlVG071TwJKu55U6_YIXn36xLtCGSKh4f5pvHf8ccYFHZYS5hXnDHdcS92ulfeGexUYbI-PzKAOG6DFCGxOFTV3vMO3KwtJi3T2zkn-T7lX5g-OgzHQiLiFZYRJIf-zGqYjb8zbPIdhA__sKTGyHJxyzKNKMqpdHNiniVNoIfioBaMyvGITx0DfE5slORml2Woq_K89XhNVKMBgGqx4faMaNA-X3eFjzBjEJsran25bjWNSXSmWebxSmOw&scope=channel_subscriptions+openid
