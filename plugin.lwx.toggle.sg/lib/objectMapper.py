from Item import Item

INTERNAL_ROUTE_PREFIX = 'plugin://plugin.lwx.toggle.sg/'

def mapSearchResultsToObjects(searchResults):
    ''' searchResults in dictionary format '''
    # fix this, we need to set videoURL to the episode url with plugin prefix
    # then add in actionsResolver in main to actually resolve to the videoURL
    items = []
    for result in searchResults:
        print(result)
        epNo = result['EpisodeNum']
        duration = result['DurationInMins']
        episodeURL = result['FullUrl']
        mediaName = result['FullMediaName']
        imageURL = 'https://www.mewatch.sg' + result['PicURL']


        item = Item()
        item.epNo = epNo
        item.duration = duration
        item.episodeURL = episodeURL
        item.epName = u'EP{} - {}'.format(','.join(epNo), mediaName)
        item.videoURL = "{}?&action=resolveVideoURL&episodeURL={}".format(INTERNAL_ROUTE_PREFIX, item.episodeURL)
        item.imageURL = imageURL
        item.subtitles = [] # stub
        items.append(item)
    return items