import requests
import json

#Send an API request, show request status, put data into dictionary, and return

def requestTxns(serverName, network, walletAddress, nextToken):
    if serverName == 'Algonode' and network == 'Mainnet':
        if nextToken == '':
            print('Txn request for: ' + walletAddress)
            response = requests.get('https://mainnet-idx.algonode.cloud/v2/accounts/' + walletAddress + '/transactions', params={'limit': '1000'})
            print('Txn request == ' + str(response))
        else:
            print('Txn request for: ' + walletAddress + ' with token: ' + nextToken)
            response = requests.get('https://mainnet-idx.algonode.cloud/v2/accounts/' + walletAddress + '/transactions', params={'next': nextToken, 'limit': '69420'})
            print('Txn request == ' + str(response))
    else: print('Currently Algonode Mainnet only')
    print('Txn data request to ' + serverName + ': Complete.')
    return response


def requestSingleAsset(assetID):


    response = requests.get('https://mainnet-idx.algonode.cloud/v2/assets/' + str(assetID)).json()
    print('Asset request for: ' + str(assetID))

    try:
        assetData = response['asset']['params']

        if 'name' in assetData: name = assetData['name']
        else: name = str(assetID)
        if 'unit-name' in assetData: unitName = assetData['unit-name']
        else: unitName = str(assetID)

        assetDB = {'name':name,
                'ticker':unitName,
                'decimals':assetData['decimals']}

        print('Request complete for: ' + name)
    except:
        assetDB = {'name':str(assetID),
                'ticker':str(assetID),
                'decimals':0}

    return assetDB


def requestManyAssets(assetDB):
    assetResponse = requests.get("https://free-api.vestige.fi/assets").json()

    for asset in assetResponse:
        if str(asset['id']) not in assetDB: 
            assetDB[str(asset['id'])] = {'name':asset['name'],
                                        'ticker':asset['ticker'],
                                        'decimals':asset['decimals']}
    print('\nAsset data request to Vestige: Complete\n')
    return assetDB


def requestAMMPools(appDB, assetDB):

    print('Sending Pool data request to Vestige')
    providersResponse = requests.get("https://free-api.vestige.fi/providers").json()

    for provider in providersResponse:
        print('Sending Pool data request to Vestige: ' + provider['name'])

        if provider['id'] in ['TM', 'T2', 'T3']:
            providerName = 'Tinyman'
        elif provider['id'] in ['PT', 'PS']:
            providerName = 'Pact'
        elif provider['id'] in ['AF', 'A2']:
            providerName = 'Algofi'
        elif provider['id'] in ['HS', 'H2']:
            providerName = 'Humble Swap'
        elif provider['id'] == 'UT':
            providerName = 'Ultrade'

        poolResponse = requests.get("https://free-api.vestige.fi/pools/" + provider['id']).json()
        for pool in poolResponse:




            if str(pool['asset_1_id']) in assetDB:
                asset1 = assetDB[str(pool['asset_1_id'])]['ticker']
            elif pool['asset_1_id'] == None:
                asset1 = 'ALGO'
            else: asset1 = pool['asset_1_id']
            if str(pool['asset_2_id']) in assetDB:
                asset2 = assetDB[str(pool['asset_2_id'])]['ticker']
            elif pool['asset_2_id'] == None:
                asset2 = 'ALGO'
            else: asset2 = pool['asset_2_id']

            if str(pool['application_id']) not in appDB:
                appDB[str(pool['application_id'])] = {"platform":providerName,"appName":str(str(asset1) + '/' + str(asset2) + ' Liquidity Pool')}
                #print(appDB[str(pool['application_id'])])


    print('AMM Pool data request to Vestige: Complete\n')
    return appDB


