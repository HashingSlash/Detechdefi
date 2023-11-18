import json
import base64
import scripts.databaseFunctions as databaseFunctions
import scripts.transactionFunctions as transactionFunctions

def buildPlatformDiagDB(requestedPlatform):
    platforms = ['Algofi', 'Yieldly', 'AlgoFund', 'Folks Finance', 'Pact', 'Tinyman', 'Vestige', 'Deflex']
    diagDB = {}
    if requestedPlatform in platforms:
        platforms = [requestedPlatform]
    for platformToLoad in platforms:
        try:
            inFile = open('platforms/' + platformToLoad + '.json', 'r')
            diagDB[platformToLoad] = json.load(inFile)
            inFile.close()
            
        except IOError:
            print('Diag IOError : ' + str(platformToLoad))

    return diagDB


txnTypeDetail = {'acfg' : 'asset-config-transaction',
                'afrz' : 'asset-freeze-transaction',
                'appl' : 'application-transaction',
                'axfer' : 'asset-transfer-transaction',
                'keyreg' : 'keyreg-transaction',
                'pay' : 'payment-transaction',
                'stpf' : 'state-proof-transaction'}


def base64decode(toDecode):
    try:
        #print(toDecode)
        encodedArg = toDecode.encode('ascii')
        convertedArg = base64.b64decode(encodedArg)
        return convertedArg.decode("ascii")
    except:
        print('decode error')
        return 'decode error'



def diagDBParse(mainDB, groupID, diagDB):

    #Grab IDs, onCompletion and application arguments from txns
    tempDB = {"groupAppIDs" : [],
        "groupAppArgs" : [],
        "groupOnComplete" : [],
        "groupPlatforms" : [],
        "groupAppGroups" : [],
        "groupActions" : []}
    
    for txnID in mainDB['groups'][groupID]['txns']:
        #load txn main body and txn-type unique body into vars
        txn = mainDB['rawTxns'][txnID]
        txnTypeDetails = txn[txnTypeDetail[txn['tx-type']]]
        #check application txns for details for diag
        if txn['tx-type'] == 'appl':
            txnAppID = txnTypeDetails['application-id']
            tempDB['groupAppIDs'] = databaseFunctions.appendToEmbeddedList(tempDB['groupAppIDs'], txnAppID)
            try:
                for foreignAppID in txnTypeDetails['foreign-apps']:
                    tempDB['groupAppIDs'] = databaseFunctions.appendToEmbeddedList(tempDB['groupAppIDs'], foreignAppID)
            except:pass

            tempDB['groupOnComplete'] = databaseFunctions.appendToEmbeddedList(tempDB['groupOnComplete'], txnTypeDetails['on-completion'])
            if txnTypeDetails['application-args'] != []:
                for txnAppArg in txnTypeDetails['application-args']:
                    tempDB['groupAppArgs'] = databaseFunctions.appendToEmbeddedList(tempDB['groupAppArgs'], txnAppArg)

            for testPlatform in diagDB:
                #for each platform in the diagDB
                for testAppGroup in diagDB[testPlatform]:
                    #for each app group in the platform listing
                    IDMatches = []
                    appGroupMatches = []
                    actionMatches = []
                    
                    #check each app group, load its IDS, then iterate through its functions
                    actionIDs = diagDB[testPlatform][testAppGroup]['IDs']
                    for txnGroupID in tempDB['groupAppIDs']:
                        #check for ID matches between this app group and the app IDs found in the Transaction group
                        if str(txnGroupID) in actionIDs:
                            ##print('ID Match')
                            #If an ID match between the App IDs from the txn group, and the Platforms App group, store the platforms name
                            if testPlatform not in IDMatches: IDMatches.append(testPlatform)
                    #check each action within each app group.

                    if len(IDMatches) >= 1:        
                        for testAction in diagDB[testPlatform][testAppGroup]['functions']:
                            actionCriteria = diagDB[testPlatform][testAppGroup]['functions'][testAction]
                            #Check through all appArgs found in the txn group
                            if 'appArgs' in actionCriteria:
                                for testArg in actionCriteria['appArgs']:
                                    if testArg in tempDB['groupAppArgs']:
                                        #if len(IDMatches) == 0: print(groupID)
                                        if testAppGroup not in appGroupMatches: appGroupMatches.append(testAppGroup)
                                        if testAction not in actionMatches: actionMatches.append(testAction)                                      
                            if 'onComplete' in actionCriteria and actionCriteria['onComplete'] in tempDB['groupOnComplete'] :
                                if testAppGroup not in appGroupMatches: appGroupMatches.append(testAppGroup)
                                if testAction not in actionMatches: actionMatches.append(testAction)
                            
                            if 'local-state-delta' in actionCriteria and 'local-state-delta' in txn: 
                                for entry in txn['local-state-delta']:
                                    if 'delta' in entry: # and 'key' in entry['delta']:
                                        for deltaEntry in entry['delta']:
                                            if 'key' in deltaEntry and deltaEntry['key'] == actionCriteria['local-state-delta']:
                                                if testAppGroup not in appGroupMatches: appGroupMatches.append(testAppGroup)
                                                if testAction not in actionMatches: actionMatches.append(testAction)

                                


                            for IDMatch in IDMatches:
                                tempDB['groupPlatforms'] = databaseFunctions.appendToEmbeddedList(tempDB['groupPlatforms'], IDMatch)
                            for groupAppMatch in appGroupMatches:
                                tempDB['groupAppGroups'] = databaseFunctions.appendToEmbeddedList(tempDB['groupAppGroups'], groupAppMatch)
                            for groupActionMatch in actionMatches:
                                tempDB['groupActions'] = databaseFunctions.appendToEmbeddedList(tempDB['groupActions'], groupActionMatch)



    return tempDB

def appDBParse(tempDB, appDB):
    if len(tempDB['groupPlatforms']) < 1:
        for appID in tempDB['groupAppIDs']:
            if str(appID) in appDB:
                tempDB['groupPlatforms'] = databaseFunctions.appendToEmbeddedList(tempDB['groupPlatforms'], appDB[str(appID)]['platform'])
                tempDB['groupActions'] = databaseFunctions.appendToEmbeddedList(tempDB['groupActions'], appDB[str(appID)]['appName'])
                tempDB['groupAppGroups'] = databaseFunctions.appendToEmbeddedList(tempDB['groupAppGroups'], 'appDB match')

    return tempDB

def parseGroups(mainDB, testing):
    print('Parsing Groups')
    #Vars

    if type(testing) == str: soloPlatform = testing
    else: soloPlatform = ''
    diagDB = buildPlatformDiagDB(soloPlatform)


    for groupID in mainDB['groups']:
        tempDB = diagDBParse(mainDB, groupID, diagDB)
        tempDB = appDBParse(tempDB, mainDB['apps'])


        platformStr = ''
        actionStr = ''
        appStr = ''

        for platform in tempDB['groupPlatforms']:
            if platformStr != '' and platform != '': platformStr = platformStr + ', '
            platformStr = platformStr + platform + ''

        for action in tempDB['groupActions']:
            if actionStr != '': actionStr = actionStr + ', '
            actionStr = actionStr + action + ''

        for appl in tempDB['groupAppGroups']:
            if appStr != '': appStr = appStr + ', '
            appStr = appStr + appl + ''

        mainDB['groups'][groupID]['platform'] = platformStr
        mainDB['groups'][groupID]['action'] = actionStr
        mainDB['groups'][groupID]['appGroup'] = appStr


    
    
    



    return mainDB





