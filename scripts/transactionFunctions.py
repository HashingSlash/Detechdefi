import datetime
import scripts.diagnosisFunctions as diagnosisFunctions
import math

def returnEmptyTxn():
    emptyTxn = {'time' : '',
                'type' : '',
                'sentCurrency' : '',
                'sentQuantity' : 0,
                'receivedCurrency' : '',
                'receivedQuantity' : 0,
                'feeCurrency' : '',
                'feeQuantity' : 0,
                'id' : '',
                'description' : ''}
    return emptyTxn

def returnTxnTypeInfo():
    txnTypeDetail = {'acfg' : ['asset-config-transaction', 'Asset Configuration'],
                    'afrz' : ['asset-freeze-transaction', 'Asset Freeze'],
                    'appl' : ['application-transaction', 'Application'],
                    'axfer' : ['asset-transfer-transaction', 'Asset Transfer'],
                    'keyreg' : ['keyreg-transaction', 'Key Registration'],
                    'pay' : ['payment-transaction', 'ALGO Transfer'],
                    'stpf' : ['state-proof-transaction', 'State Proof']}
    return txnTypeDetail

def returnAssetMovements(rawTxn, txnSpecs, walletID, txnToReturn):

    if rawTxn['sender'] == walletID:
        if rawTxn['tx-type'] in ['pay', 'axfer']:
            txnToReturn['sentQuantity'] = txnSpecs['amount']
            if rawTxn['tx-type'] == 'pay':
                txnToReturn['sentCurrency'] = 'ALGO'
            elif rawTxn['tx-type'] == 'axfer':
                txnToReturn['sentCurrency'] = txnSpecs['asset-id']

        
    elif 'receiver' in txnSpecs and txnSpecs['receiver'] == walletID:
            txnToReturn['receivedQuantity'] = txnSpecs['amount']
            if rawTxn['tx-type'] == 'pay':
                txnToReturn['receivedCurrency'] = 'ALGO'
            elif rawTxn['tx-type'] == 'axfer':
                txnToReturn['receivedCurrency'] = txnSpecs['asset-id']


    return txnToReturn

def returnInnerTxns(rawTxn, walletID, innerTxns, refID, description):
    txnTypeDetail = returnTxnTypeInfo()
    if 'inner-txns' in rawTxn:
        for innerTxn in rawTxn['inner-txns']:
            innerDetails = innerTxn[txnTypeDetail[innerTxn['tx-type']][0]]
            processedInner = returnAssetMovements(innerTxn, innerDetails, walletID, returnEmptyTxn())

            processedInner['time'] = str(datetime.datetime.fromtimestamp(rawTxn['round-time']))
            processedInner['id'] = 'InnerTxn - ' + refID
            processedInner['description'] = description

            if processedInner['sentQuantity'] + processedInner['receivedQuantity'] !=0:
                innerTxns.append(processedInner)
            innerTxns = returnInnerTxns(innerTxn, walletID, innerTxns, str('Inner ' + refID), description + ' ')


    return innerTxns

def buildGroupRow(groupID, mainDB):
    groupTxn = returnEmptyTxn()
    groupEntry = mainDB['groups'][groupID]
    description = str(len(groupEntry['txns'])) + ' txns. '
    groupTxnList = []
    txnTypeDetail = returnTxnTypeInfo()

    

    if groupEntry['platform'] != '':
        description = description + str(groupEntry['platform']) + ' : ' + groupEntry['appGroup'] + ' : ' + str(groupEntry['action'])


    groupTime = str(datetime.datetime.fromtimestamp(groupEntry['round-time']))
    groupTxn['time'] = groupTime
    groupTxn['id'] = groupID
    groupTxn['description'] = description

    comboTxnList = []



    txnNumber = 0
    for txnID in groupEntry['txns']:

        txnSpecs = mainDB['rawTxns'][txnID][txnTypeDetail[mainDB['rawTxns'][txnID]['tx-type']][0]] 
        txnNumber += 1

        if mainDB['rawTxns'][txnID]['sender'] == mainDB['wallet'] and mainDB['rawTxns'][txnID]['fee'] > 0:
            groupTxn['feeQuantity'] = groupTxn['feeQuantity'] + mainDB['rawTxns'][txnID]['fee']
            groupTxn['feeCurrency'] = 'ALGO'



        for txn in buildSingleRow(mainDB['rawTxns'][txnID], mainDB, description + ' '):
            if txn['sentQuantity'] != 0 or txn['receivedQuantity'] != 0 or txn['feeQuantity'] != 0:
                groupTxnList.append(txn)

    ####-------------------------------------------

    

    #for txn in groupTxnList:
    #    combinedTxn = returnEmptyTxn()
    #    combinedTxn['description'] = description
    #    combinedTxn['time'] = groupTime
    #    combinedTxn['id'] = 'Group txn ' + str(len(comboTxnList) + 1) + ': ' + groupID
#
#        combinedTxn['sentQuantity'] = txn['sentQuantity']
#        combinedTxn['sentCurrency'] = txn['sentCurrency']
#
#
#        combinedTxn['receivedQuantity'] = txn['receivedQuantity']
#        combinedTxn['receivedCurrency'] = txn['receivedCurrency']
#
#
#        combinedTxn['feeQuantity'] = txn['feeQuantity']
#        combinedTxn['feeCurrency'] = txn['feeCurrency']


        
#        comboTxnList.append(combinedTxn)


    return groupTxnList

def buildSingleRow(rawTxn, mainDB, description):
    txnTypeDetail = returnTxnTypeInfo()
    txnSpecs = rawTxn[txnTypeDetail[rawTxn['tx-type']][0]]

    singleTxn = returnAssetMovements(rawTxn, txnSpecs, mainDB['wallet'], returnEmptyTxn())

    if 'group' in rawTxn: 
        group = True
        singleTxn['id'] = 'G-' + str(rawTxn['group'][:5]) + ' - ' + rawTxn['id']
    else:
        group = False
        singleTxn['id'] = rawTxn['id']

    if rawTxn['sender'] == mainDB['wallet'] and 'receiver' in txnSpecs and txnSpecs['receiver'] == mainDB['wallet']:
        description = 'Asset Opt in/out'

    elif rawTxn['sender'] == mainDB['wallet']:
        if group == False: description = description + 'Sender'
        if rawTxn['fee'] > 0:
            singleTxn['feeCurrency'] = 'ALGO'
            singleTxn['feeQuantity'] = rawTxn['fee']

    elif 'receiver' in txnSpecs and txnSpecs['receiver'] == mainDB['wallet']:
        if group == False: description = description + 'Receiver'

    innerTxns = returnInnerTxns(rawTxn, mainDB['wallet'], [], rawTxn['id'][:5], description)


    singleTxn['time'] = str(datetime.datetime.fromtimestamp(rawTxn['round-time']))
    singleTxn['description'] = description
    

    

    txnList = [singleTxn]




    i = 0
    for innerTxn in innerTxns:
        i += 1
        innerTxn['id'] = 'in' + str(i) + ' ' + innerTxn['id']
        txnList.append(innerTxn)
  


    return txnList

def logPriceCheck(pricesToCheck, asset, roundNumber):
    if asset not in pricesToCheck:
        pricesToCheck[asset] = {}
    if roundNumber not in pricesToCheck:
        pricesToCheck[asset][roundNumber] = {}

    pricesToCheck['total'] = pricesToCheck['total'] + 1

    return pricesToCheck

def assembleTransactions(mainDB, testing):
    processedGroups = []
    #ALGO, USDC, USDT
    #prices that most cryto-places can derive
    commonPrices = ['ALGO', '31566704', '312769']
    pricesToCheck = {'total':0}
    

    for txnID in mainDB['txnOrder']:
        rawTxn = mainDB['rawTxns'][txnID]

        if 'group' not in rawTxn:
            roundRows = buildSingleRow(rawTxn, mainDB, '')

            
        elif rawTxn['group'] not in processedGroups:
            roundRows = buildGroupRow(rawTxn['group'], mainDB)
            processedGroups.append(rawTxn['group'])
        

        for row in roundRows:
            
            if row['sentCurrency'] not in commonPrices and row['receivedCurrency'] not in commonPrices:
                if row['sentCurrency'] != '': mainDB['prices'] = logPriceCheck(pricesToCheck, str(row['sentCurrency']), str(rawTxn['confirmed-round']))
                if row['receivedCurrency'] != '': mainDB['prices'] = logPriceCheck(pricesToCheck, str(row['receivedCurrency']), str(rawTxn['confirmed-round']))
            if row['feeCurrency'] not in commonPrices:
                if row['feeCurrency'] != '': mainDB['prices'] = logPriceCheck(pricesToCheck, str(row['feeCurrency']), str(rawTxn['confirmed-round']))
            


            mainDB['txnRounds'][str(rawTxn['confirmed-round'])][row['id']] = row



    return mainDB

def convertCurrency(figureToConvert, decimals):

    figureToConvert = figureToConvert / math.pow(10, decimals)
    figureToConvert = f'{figureToConvert:.8f}'

    return figureToConvert.rstrip('0')

def convertAssetInfo(convertTxn, assetDB):


    if 'sentQuantity' in convertTxn and convertTxn['sentQuantity'] >= 0:
        if convertTxn['sentCurrency'] == 'ALGO':
            convertTxn['sentQuantity'] = convertCurrency(int(convertTxn['sentQuantity']), 6)
        elif convertTxn['sentCurrency'] != '':

            convertTxn['sentQuantity'] = convertCurrency(int(convertTxn['sentQuantity']), int(assetDB[str(convertTxn['sentCurrency'])]['decimals']))
            convertTxn['sentCurrency'] = assetDB[str(convertTxn['sentCurrency'])]['ticker']
            


    if 'receivedQuantity' in convertTxn and convertTxn['receivedQuantity'] >= 0:
        if convertTxn['receivedCurrency'] == 'ALGO':
            convertTxn['receivedQuantity'] = convertCurrency(int(convertTxn['receivedQuantity']), 6)
        elif convertTxn['receivedCurrency'] != '':
            convertTxn['receivedQuantity'] = convertCurrency(int(convertTxn['receivedQuantity']), int(assetDB[str(convertTxn['receivedCurrency'])]['decimals']))
            convertTxn['receivedCurrency'] = assetDB[str(convertTxn['receivedCurrency'])]['ticker']


    if 'feeCurrency' in convertTxn and convertTxn['feeQuantity'] >= 0:
        if convertTxn['feeCurrency'] == 'ALGO':
            convertTxn['feeQuantity'] = convertCurrency(int(convertTxn['feeQuantity']), 6)
        elif convertTxn['feeCurrency'] != '':
            convertTxn['feeCurrency'] = convertCurrency(int(convertTxn['feeCurrency']), int(assetDB[str(convertTxn['feeCurrency'])]['decimals']))
            convertTxn['feeCurrency'] = assetDB[str(convertTxn['feeCurrency'])]['ticker']   

    return convertTxn

