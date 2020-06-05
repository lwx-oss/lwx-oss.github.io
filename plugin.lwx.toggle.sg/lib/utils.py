import requests
import xbmc


def search(searchTerm, pageIndex = 0):
    cookies = {
        'UID': '614f5c0a-b62a-490d-80c1-878ce36f2695',
        'MeID_Seg': 'none',
        'adtechTargetingKeys': 'none',
        'volumeControl_volumeValue': '0',
        'visid_incap_2170514': 'Y9jWDjNKQP2NvukX40SZBxKG2F4AAAAAQUIPAAAAAABER9uhAtKV+eTiXLhY/EXL',
        'incap_ses_168_2170514': 'AmLgBhCS9i8hIjkKTdtUAhOG2F4AAAAABJoJCkf3QnShM1hMJEDCMw==',
        'incap_ses_990_2170514': 'NNocO3rHIG2T0pSMwy+9DRSG2F4AAAAAoD92B8Tml4Yh5WnmEyAwBQ==',
    }

    headers = {
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.mewatch.sg/en/search?q={}&section=video'.format(searchTerm),
        'Accept-Language': 'en-US,en;q=0.9',
    }

    params = (
        ('text', '{}'.format(searchTerm)),
        ('mediaType', 'Episode'),
        ('sortBy', ''),
        ('sortDirection', ''),
        ('pageIndex', '{}'.format(pageIndex)),
        ('tgPage', '5007044'),
        ('filterList', ''),
    )

    response = requests.get('https://www.mewatch.sg/en/blueprint/servlet/togglev3/search', headers=headers, params=params, cookies=cookies)

    return response.json()


def iterativeSearch(searchTerm):
    # import web_pdb; web_pdb.set_trace()

    pageIndex = 0
    allResults = []

    results = search(searchTerm)

    allResults += results['list']

    totalResults = int(results['totalResult'])

    totalPages = int(totalResults / 10) + 1

    while totalPages - 1 != pageIndex:
        pageIndex += 1
        nextPage = search(searchTerm, pageIndex)
        allResults += nextPage['list']

    return allResults
        


def getInput(heading='Enter your search term:'):
    kb = xbmc.Keyboard('default', 'heading', True)
    kb.setHeading(heading)
    kb.setDefault('')
    kb.setHiddenInput(False)
    kb.doModal()

    inputValue = None

    if(kb.isConfirmed()):
        inputValue = kb.getText()
    
    return inputValue
