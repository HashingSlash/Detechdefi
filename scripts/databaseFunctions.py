import scripts.requestFunctions as requestFunctions
import scripts.transactionFunctions as transactionFunctions
import json
import csv


def appendToEmbeddedList(list, entry):
    #im sure there is a more affective way to do this
    #however this saved a lot of redundancy for now
    if entry not in list:
        list.append(entry)
    return list

def createDatabases(tempDB):
    #This function fills the main DB with data from transactions
    txnTypeDetail = transactionFunctions.returnTxnTypeInfo()
    rawTxnDB = tempDB['rawTxns']
    txnOrder = []
    for txnID in rawTxnDB:
        txn = rawTxnDB[txnID]
        #set Transaction variables
        txnType = txn['tx-type']
        txnSpecs = txn[txnTypeDetail[txnType][0]]
        txnRound = str(txn['confirmed-round'])

        #txnRound
        #make an entry for each txn round that appears in the processed txns. Not all will be needed.
        #txnOrder is also used to help keep txn groups in order, as they will all share a txn round number.
        txnOrder.insert(0, txnID)
        if txnRound not in tempDB['txnRounds']:
            tempDB['txnRounds'][txnRound] = {}

        #txnGroup
        #make a txn group database entry
        if 'group' in txn:
            txnGroupID = txn['group']
            if txn['group'] not in tempDB['groups']:
                tempDB['groups'][txnGroupID] = {'txns' : [], 'platform':'', 'action': '', 'appGroup' : '', 'round-time' : txn['round-time']}
            #add the txn ids to txn group entry. Not all will be needed.
            if txnID not in tempDB['groups'][txnGroupID]['txns']:
                tempDB['groups'][txnGroupID]['txns'].insert(0, txnID)

        #txnAsset
        #create a database entry for each Asset that appears in the processed transactions
        if txnType == 'axfer':
            txnAssetID = str(txnSpecs['asset-id'])
            if txnAssetID not in tempDB['assets']:
                tempDB['assets'][txnAssetID] = {}
        #also check for assets in inner txns. Sometimes an asset may be utilized without even appearing in a axfer txn.
        #one example of this is with swap routers, as capital may flow through an asset the account never deals with other wise.
        #this may all be abstracted away into inner txns.
        if 'inner-txns' in txn:
            for innerTxn in txn['inner-txns']:
                if innerTxn['tx-type'] == 'axfer':
                    txnAssetID = str(innerTxn['asset-transfer-transaction']['asset-id'])
                    if txnAssetID not in tempDB['assets']:
                        tempDB['assets'][txnAssetID] = {}

    tempDB['txnOrder'] = txnOrder

    #for each blank asset entry, get its details from AlgoNode
    for assetID in tempDB['assets']:
        if tempDB['assets'][str(assetID)] == {}:
            tempDB['assets'][str(assetID)] = requestFunctions.requestSingleAsset(str(assetID))


    return tempDB

def fetchTxns(node, network, tempDB):
    #set some intial variables
    fetchComplete = False
    tempResponse = requestFunctions.requestTxns(node, network, tempDB['wallet'], '')
    response = tempResponse.json()

    #use a loop to keep checking for txns until all received.
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
    #this loads the appIDs csv file in /resources into the programs main database
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
    #this loads the assets csv file in /resources into the programs main database
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

def initAddressDB(tempAddressDB):
    #this loads the assets csv file in /resources into the programs main database
    try:
        inFile = open('resources/addressBook.csv', 'r', encoding='utf-8')
        reader = csv.reader(inFile)
        headerLine = True
        for line in reader:
            if headerLine == True:
                headerLine = False
                continue
            if str(line[0]) not in tempAddressDB:
                tempAddressDB[str(line[0])] = {'name': line[1], 'usage':line[2]}
        print('Loaded Address Book: resources/addressBook.csv')
    except:
        print('Fresh address book')

    return tempAddressDB

def initMainDB():
    NFDData = None
    #either load previous database or build a new one
    walletID = None
    try:
        inFile = open('resources/db.json', 'r')
        tempDB = json.load(inFile)
        #print('Loaded main database')
        #print('Asset data loaded: ' + str(len(tempDB['assets'])) + '. Application data loaded: ' + str(len(tempDB['apps'])))
        inFile.close()
        initial_input = input('Change wallet from: ' + tempDB['walletName'] + ' ? (Y/N): ').upper()
        if initial_input != 'Y':
            walletID = tempDB['wallet']
        else:
            tempDB = None
        if initial_input != '' and tempDB != None and input('Rebuild database (Y/N): ').upper() == 'Y':
            tempDB = None
    except IOError: #database load failed. prompt user to input wallet address to init new database
        tempDB = None

    if walletID == None:
        walletID = input('Wallet address or NFD: ')
    if tempDB == None:
        combineRows = True
        NFDData = None
        try:
            if walletID[-5:] == '.algo':
                walletName = walletID
                NFDData = requestFunctions.requestNFDAddressData(walletName)
                walletID = NFDData['owner']
            else:
                try:
                    walletName = requestFunctions.requestAddressNFDData(walletID)
                except:
                    walletName = walletID[:7]
        except:
            walletName = walletID[:7]


        ####                Init db
        #   Using db as a main dictionary to hold all relevant data as sub-dictionaries.
        print('Init new database')
        tempDB = {'wallet':walletID,     #str    - wallet public key (address)
            'walletName':walletName,
            'combineRows': combineRows,
            'rawTxns': {},             #transaction id : raw/'on-chain' transaction data}
            'txnRounds': {},           #
            'groups': {},              #group txn data, for automated group txn identifaction
            'assets': {}, #Mainnet asset data such as tickers, IDs, names, decimals.
            'apps': {},
            'addressBook': {}}     #mainnet app IDs. This helps identify some txn groups
        
        #below script checks and adds current popular assets via Vestige API calls
        tempDB['assets'] = requestFunctions.requestManyAssets(tempDB['assets'])
        #print('Asset data loaded: ' + str(len(tempDB['assets'])) + '. Application data loaded: ' + str(len(tempDB['apps'])))

    
        

    else:
        tempDB['txnRounds'] = {}
        tempDB['groups'] = {}

    tempDB['assets'] = initAssetDB({})
    tempDB['apps'] = initAppDB({})
    tempDB['addressBook'] = initAddressDB({})

    if NFDData != None:
        if NFDData['appID'] not in tempDB['apps']:
            tempDB['apps'][str(NFDData['appID'])] = {"platform":'NF Domains',"appName":NFDData['name']}
        if NFDData['asaID'] not in tempDB['assets']:
            tempDB['assets'][str(NFDData['asaID'])] = requestFunctions.requestSingleAsset(NFDData['asaID'])
        if NFDData['nfdAccount'] not in tempDB['addressBook']:
            tempDB['addressBook'][NFDData['nfdAccount']] = {"name":'NF Domains','usage': str(NFDData['name'])}


    if initial_input != '' and input('Update apps and assets via Vestige? (Y/N): ').upper() == 'Y':
        tempDB = requestFunctions.requestAMMPools(tempDB)

    return tempDB

def countMatchedGroups(groupDB, testing):
    ##this function counts txn group matches
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
        print('\nMatched Groups: ' + str(matchedGroups) + '\nTotal # Groups: ' + str(len(groupDB)) + '\nMatched %: ' + str(round(matchedGroups / len(groupDB)*100, 2)))


    return counts

