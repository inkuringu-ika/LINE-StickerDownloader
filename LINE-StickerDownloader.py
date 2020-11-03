import urllib
import requests
import json
from tqdm import tqdm
import sys
import traceback

lang = 'en-US'
UserAgent = "LINE/10.17.0 (iPhone; iOS 14.1; Scale/2.00)"

headers = {
    'user-agent':UserAgent,
    'accept':'*/*',
    'accept-language':lang,
    'accet-encoding':'identity'
    }

input_url = input("StickerShopURL: ")
input_url_parsed = urllib.parse.urlparse(input_url)
if(input_url_parsed.netloc == "store.line.me"):
    if(input_url_parsed.path.split("/")[1] == "stickershop"):
        stickerId = input_url_parsed.path.split("/")[3]
    else:
        print('Error: Unsupported type "' + input_url_parsed.path.split("/")[1] + '"')
        sys.exit(1)
else:
    print("Error: URL is wrong")
    sys.exit(1)

response = requests.get("https://stickershop.line-scdn.net/stickershop/v1/product/" + stickerId + "/IOS/productInfo.meta",headers=headers)
response.raise_for_status()
json_result = json.loads(response.text)

'''
hasSound
hasAnimation
hasPopup   (https://static.line-scdn.net/line_store/16909542e95/thrift/thrift.js)

stickerResourceType (https://static.line-scdn.net/line_store/16909542e95/thrift/thrift.js)
1 : STATIC
2 : ANIMATION
3 : SOUND
4 : ANIMATION_SOUND
5 : POPUP
6 : POPUP_SOUND
? : NAME_TEXT   (https://store.line.me/officialaccount/event/sticker/18126/ja)
? : PER_STICKER_TEXT   (https://store.line.me/officialaccount/event/sticker/18637/ja)
'''

if((("hasSound" in json_result) and json_result["hasSound"]) or (("stickerResourceType" in json_result) and ("sound" in json_result["stickerResourceType"].lower()))):
    has_sound = True
else:
    has_sound = False

if((("hasAnimation" in json_result) and json_result["hasAnimation"]) or (("stickerResourceType" in json_result) and ("animation" in json_result["stickerResourceType"].lower()))):
    has_animation = True
else:
    has_animation = False

if((("hasPopup" in json_result) and json_result["hasPopup"]) or (("stickerResourceType" in json_result) and ("popup" in json_result["stickerResourceType"].lower()))):
    has_popup = True
else:
    has_popup = False

if(("stickerResourceType" in json_result) and ("name_text" in json_result["stickerResourceType"].lower())):
    is_custom_text = True
else:
    is_custom_text = False

if(("stickerResourceType" in json_result) and ("per_sticker_text" in json_result["stickerResourceType"].lower())):
    is_free_text = True
else:
    is_free_text = False

if(has_sound or has_animation or has_popup or is_custom_text or is_free_text):
    request_url = 'https://stickershop.line-scdn.net/stickershop/v1/product/' + stickerId + '/IOS/stickerpack@2x.zip'
else:
    request_url = 'https://stickershop.line-scdn.net/stickershop/v1/product/' + stickerId + '/IOS/stickers@2x.zip'

response = requests.get(request_url, stream=True,headers=headers)
response.raise_for_status()
pbar = tqdm(total=int(response.headers["content-length"]), unit="B", unit_scale=True)
with open(stickerId + ".zip", 'wb') as file:
    for chunk in response.iter_content(chunk_size=1024):
        file.write(chunk)
        pbar.update(len(chunk))
    pbar.close()
