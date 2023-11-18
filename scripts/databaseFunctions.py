import scripts.requestFunctions as requestFunctions
import scripts.transactionFunctions as transactionFunctions
import json
import csv



def appendToEmbeddedList(list, entry):
    if entry not in list:
        list.append(entry)
    return list

def createDatabases(tempDB):
    txnTypeDetail = transactionFunctions.returnTxnTypeInfo()
    rawTxnDB = tempDB['rawTxns']
    txnOrder = []
    for txnID in rawTxnDB:
        txn = rawTxnDB[txnID]
        #Transaction variables
        txnType = txn['tx-type']
        txnSpecs = txn[txnTypeDetail[txnType][0]]
        txnRound = str(txn['confirmed-round'])

        #txnRound
        txnOrder.insert(0, txnID)
        if txnRound not in tempDB['txnRounds']:
            tempDB['txnRounds'][txnRound] = {}

        #txnGroup

        if 'group' in txn:
            txnGroupID = txn['group']
            if txn['group'] not in tempDB['groups']:
                tempDB['groups'][txnGroupID] = {'txns' : [], 'platform':'', 'action': '', 'appGroup' : '', 'round-time' : txn['round-time']}

            if txnID not in tempDB['groups'][txnGroupID]['txns']:
                tempDB['groups'][txnGroupID]['txns'].insert(0, txnID)


        #txnAsset
        if txnType == 'axfer':
            txnAssetID = str(txnSpecs['asset-id'])
            if txnAssetID not in tempDB['assets']:
                tempDB['assets'][txnAssetID] = {}

        if 'inner-txns' in txn:
            for innerTxn in txn['inner-txns']:
                if innerTxn['tx-type'] == 'axfer':
                    txnAssetID = str(innerTxn['asset-transfer-transaction']['asset-id'])
                    if txnAssetID not in tempDB['assets']:
                        tempDB['assets'][txnAssetID] = {}
                #else: print(innerTxn['tx-type'])

    tempDB['txnOrder'] = txnOrder

    for assetID in tempDB['assets']:
        if tempDB['assets'][str(assetID)] == {}:
            tempDB['assets'][str(assetID)] = requestFunctions.requestSingleAsset(str(assetID))


    return tempDB

def fetchTxns(node, network, tempDB):
    fetchComplete = False
    tempResponse = requestFunctions.requestTxns(node, network, tempDB['wallet'], '')
    response = tempResponse.json()

    while fetchComplete == False and str(tempResponse) == '<Response [200]>':
        for txn in response['transactions']:
            if txn['id'] not in tempDB['rawTxns']: #New txns only
                #Store txn data
                tempDB['rawTxns'][txn['id']] = txn
            else:#Finished getting new transactions, exit. Flag to also exit while loop
                fetchComplete = True
                break
        #Exit txn fetching unless there are more to request
        if fetchComplete == True: break
        if 'next-token' in response: #This means there may be more txns to request
            tempResponse = requestFunctions.requestTxns(node, network, tempDB['wallet'], response['next-token'])
            response = tempResponse.json()
        else: break #Should have all transactions now.
    return tempDB

def initAppDB(tempAppDB):
    try:
        inFile = open('resources/appIDs.csv', 'r', encoding='utf-8')
        reader = csv.reader(inFile)
        headerLine = True
        for line in reader:
            if headerLine == True:
                headerLine = False
                continue
            if line[0] not in tempAppDB:
                tempAppDB[str(line[0])] = {'platform': line[1], 'appName': line[2]}
        print('Loaded Application Database: resources/appIDs.csv')
    except:
        print('fresh appID DB')
    return tempAppDB

def initAssetDB(tempAssetDB):
    try:
        inFile = open('resources/assets.csv', 'r', encoding='utf-8')
        reader = csv.reader(inFile)
        headerLine = True
        for line in reader:
            if headerLine == True:
                headerLine = False
                continue
            if str(line[0]) not in tempAssetDB:
                tempAssetDB[str(line[0])] = {'name': line[1], 'ticker': line[2], 'decimals' : line[3]}
        print('Loaded Asset Database: resources/assets.csv')
    except:
        print('fresh assetID DB')

    return tempAssetDB

def initMainDB():
    try:
        inFile = open('resources/db.json', 'r')
        tempDB = json.load(inFile)
        print('Loaded main database')
        print('Asset data loaded: ' + str(len(tempDB['assets'])) + '. Application data loaded: ' + str(len(tempDB['apps'])))
        inFile.close()

    except IOError: #database load failed. prompt user to input wallet address to init new database
    ####                Init db
    #   Using db as a main dictionary to hold all relevant data as sub-dictionaries.
        print('Init new database')
        tempDB = {'wallet':input('Paste wallet address: '),     #str    - wallet public key (address)
            'rawTxns': {},                          #dict   - {transaction id : raw/'on-chain' transaction data}
            'txnRounds': {},
            'groups': {},
            'assets': initAssetDB({}),
            'apps': initAppDB({})}

        #tempDB['apps'] = requestFunctions.requestAMMPools(tempDB['apps'], tempDB['assets'])
        
        tempDB['assets'] = requestFunctions.requestManyAssets(tempDB['assets'])
        print('Asset data loaded: ' + str(len(tempDB['assets'])) + '. Application data loaded: ' + str(len(tempDB['apps'])))
        
    
    
    

    return tempDB

def countMatchedGroups(groupDB, testing):
    ##count matches
    counts = {}
    matchedGroups = 0

    for groupID in groupDB:
        if ',' in groupDB[groupID]['platform']: groupPlatform = 'Multiplatform'
        else: groupPlatform = groupDB[groupID]['platform']
        groupAction = groupDB[groupID]['action']
        if str(groupPlatform) not in counts: counts[str(groupPlatform)] = {}
        if str(groupAction) not in counts[str(groupPlatform)]: counts[str(groupPlatform)][str(groupAction)] = 1
        else: counts[str(groupPlatform)][str(groupAction)] += 1

        if groupPlatform != '': matchedGroups += 1




    #print counts
    if testing != False:
        for platform in counts:
            print('\n' + platform + ':   --------------')

            for action in counts[platform]:
                print(action + ': ' + str(counts[platform][action]))

    if matchedGroups != 0:
        print('\nMatched Groups: ' + str(matchedGroups) + '\nUnmatched Groups: ' + str(len(groupDB)) + '\nMatched %: ' + str(round(matchedGroups / len(groupDB)*100, 2)))


    return counts
