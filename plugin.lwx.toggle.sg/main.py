import sys
sys.path.insert(0, sys.path[1] + '/lib')  # somehow needed for importing

import xbmc
import xbmcgui
import xbmcplugin
import requests
import utils
import objectMapper
from Item import Item
from urlparse import parse_qsl
import json

_url = sys.argv[0]
# required for pinpointing plugin, treat as a pointer to the plugin instance
_handle = int(sys.argv[1])



def main():
    searchTerm = utils.getInput()
    if searchTerm == "":
        return
    searchResults = utils.iterativeSearch(searchTerm)
    items = objectMapper.mapSearchResultsToObjects(searchResults)
    createNewDirectory()
    for item in items:
        addItemToDirectory(item, 'true')
    endDirectoryCreation()


def initDirectory():
    createNewDirectory()
    # addItemToDirectory(mediaLinks)
    endDirectoryCreation()


def createNewDirectory():
    xbmcplugin.setContent(_handle, 'videos')


def endDirectoryCreation():
    xbmcplugin.endOfDirectory(_handle)


def addItemToDirectory(item, playable='false'):
    xbmcItem = _buildVideoItem(item, playable)
    xbmcplugin.addDirectoryItem(_handle, item.videoURL, xbmcItem, False)


def _buildVideoItem(item, playable):
    listItem = xbmcgui.ListItem(label=item.epName)
    listItem.setInfo('video', {'title': item.epName,
                               'genre': item.epName,
                               'mediatype': 'video'})

    listItem.setArt({
        'thumb': item.imageURL
    })

    listItem.setProperty('IsPlayable', playable)

    listItem.setSubtitles(item.subtitles)

    return listItem


def fetchAPIData(referer):

    mediaId = referer.split('/')[-1]

    headers = {
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'Origin': 'https://www.mewatch.sg',
        'Sec-Fetch-Dest': 'empty',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Referer': '{}'.format(referer),
        'Accept-Language': 'en-US,en;q=0.9',
    }

    params = (
        ('m', 'GetMediaInfo'),
    )

    data = '{"initObj":{"Platform":"Web","SiteGuid":"","DomainID":"0","UDID":"","ApiUser":"tvpapi_147","ApiPass":"11111","Locale":{"LocaleLanguage":"","LocaleCountry":"","LocaleDevice":"","LocaleUserState":"Unknown"}},"MediaID":"' + mediaId + '"}'

    response = requests.post(
        'https://tvpapi-as.ott.kaltura.com/v3_9/gateways/jsonpostgw.aspx', headers=headers, params=params, data=data)

    episodeResponse = response.json()

    showName = episodeResponse['MediaName']
    videoURL = _getBestVideoFileURL(episodeResponse['Files'])

    shortTitle = ''

    for meta in episodeResponse['Metas']:
        if meta['Key'] == "Short title":
            shortTitle = meta['Value']

    imageURL = episodeResponse['Pictures'][-1]['URL']

    epNo = ""

    for meta in episodeResponse['Metas']:
        if meta['Key'] == "Episode number":
            epNo = meta['Value']

    epName = ""
    for meta in episodeResponse['Metas']:
        if meta['Key'] == "Episode name":
            epName = meta['Value']

    subtitles = getSubtitles(referer, mediaId)

    item = Item()
    item.showName = showName
    item.videoURL = videoURL
    item.shortTitle = shortTitle
    item.imageURL = imageURL
    item.epNo = epNo
    item.epName = epName
    item.subtitles = subtitles

    return item


def _getBestVideoFileURL(files):
    ''' Cannot take the last format as best 
        Do a linear search for a pre-defined list of formats that are expected
        to be good.
    '''

    accepted = [
        'HLS_Web_Clear',
        'DASH_TV_4K',
        'DASH_Web',
        'HLS_TV'
    ]

    for format in accepted:
        for file in files:
            if file['Format'] == format:
                return file['URL']

    # use as fallback in case nothing matches, should not happen
    return files[-1]


def getSubtitles(referer, mediaId):
    headers = {
        'authority': 'sub.toggle.sg',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'sec-fetch-dest': 'empty',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'origin': 'https://www.mewatch.sg',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'referer': '{}'.format(referer),
        'accept-language': 'en-US,en;q=0.9',
    }

    params = (
        ('mediaId', mediaId),
    )

    response = requests.get(
        'https://sub.toggle.sg/toggle_api/v1.0/apiService/getSubtitleFilesForMedia', headers=headers, params=params)

    subtitlesResponse = response.json()

    subtitles = _getAllSubtitles(subtitlesResponse)

    return subtitles


def _getAllSubtitles(resp):
    subtitles = []

    for subtitle in resp['subtitleFiles']:
        subtitles.append(subtitle['subtitleFileUrl'])

    return subtitles


def populateDirectory(mediaLinks):
    for mediaLink in mediaLinks:
        item = fetchAPIData(mediaLink)
        addItemToDirectory(item)


def resolveVideoURL(episodeURL):
    item = fetchAPIData(episodeURL)
    listItem = xbmcgui.ListItem(path=item.videoURL)
    listItem.setSubtitles(item.subtitles)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listItem)


'''
actions in string to function mapping
'''

actionsList = {
    'resolveVideoURL': resolveVideoURL
}

'''
update when needed to add in more router actions
'''


def _transformRouterParamsIntoDict(params):
    d = {}

    for i in params:
        d[i[0]] = i[1]

    return d


def router(params):
    paramsDict = _transformRouterParamsIntoDict(params)
    print("Router actions,", paramsDict)
    actionsList[paramsDict['action']](paramsDict['episodeURL'])


if __name__ == '__main__':
    if sys.argv[2] != '':
        qs = sys.argv[2]
        router(parse_qsl(qs))
    else:
        main()
