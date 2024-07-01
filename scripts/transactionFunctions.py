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
                'description' : '',
                'txn partner' : ''}
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
        if rawTxn['tx-type'] in ['pay', 'axfer'] and txnSpecs['amount'] != 0:
            txnToReturn['sentQuantity'] = txnSpecs['amount']
            if rawTxn['tx-type'] == 'pay':
                txnToReturn['sentCurrency'] = 'ALGO'
            elif rawTxn['tx-type'] == 'axfer':
                txnToReturn['sentCurrency'] = txnSpecs['asset-id']
            txnToReturn['type'] = 'Send'
            txnToReturn['txn partner'] = txnSpecs['receiver']

        
    elif 'receiver' in txnSpecs and txnSpecs['receiver'] == walletID:
            if txnSpecs['amount'] != 0:
                txnToReturn['receivedQuantity'] = txnSpecs['amount']
                if rawTxn['tx-type'] == 'pay':
                    txnToReturn['receivedCurrency'] = 'ALGO'
                elif rawTxn['tx-type'] == 'axfer':
                    txnToReturn['receivedCurrency'] = txnSpecs['asset-id']
                txnToReturn['type'] = 'Receive'
                txnToReturn['txn partner'] = rawTxn['sender']


    return txnToReturn

def returnInnerTxns(rawTxn, walletID, innerTxns, refID, description):
    txnTypeDetail = returnTxnTypeInfo()
    if 'inner-txns' in rawTxn:
        for innerTxn in rawTxn['inner-txns']:
            innerDetails = innerTxn[txnTypeDetail[innerTxn['tx-type']][0]]
            processedInner = returnAssetMovements(innerTxn, innerDetails, walletID, returnEmptyTxn())

            processedInner['time'] = str(datetime.datetime.fromtimestamp(rawTxn['round-time']))
            processedInner['id'] = 'InnerTxn - ' + refID + '...'
            if 'group' in rawTxn: 
                processedInner['id'] = '(Group- ' + str(rawTxn['group'][:5]) + '...) - ' + processedInner['id']
            processedInner['description'] = description

            if processedInner['sentQuantity'] + processedInner['receivedQuantity'] !=0:
                innerTxns.append(processedInner)
            innerTxns = returnInnerTxns(innerTxn, walletID, innerTxns, str('Inner ' + refID), description + ' ')


    return innerTxns

def buildGroupRow(groupID, mainDB):
    combineRows = False
    groupTxn = returnEmptyTxn()
    comboRow = returnEmptyTxn()
    groupEntry = mainDB['groups'][groupID]
    description = str(len(groupEntry['txns'])) + ' txns. '
    groupTxnList = []
    txnTypeDetail = returnTxnTypeInfo()

    if groupEntry['platform'] != '':
        description = description + str(groupEntry['platform']) + ' : ' + groupEntry['appGroup'] + ' : ' + str(groupEntry['action'])


    groupTime = str(datetime.datetime.fromtimestamp(groupEntry['round-time']))
    comboRow['time'] = groupTime
    comboRow['description'] = description
    comboRow['id'] = 'Group - ' + groupID
    comboFeeRow = comboRow
    comboFeeRow['type'] = 'Fee'
    comboFeeRow['id'] = 'Group Combined Fees - ' + groupID
    comboFeeRow['txn partner'] = 'Algorand Network'

    comboTxnList = []

    txnNumber = 0
    for txnID in groupEntry['txns']:

        txnSpecs = mainDB['rawTxns'][txnID][txnTypeDetail[mainDB['rawTxns'][txnID]['tx-type']][0]] 
        txnNumber += 1

        for txn in buildSingleRow(mainDB['rawTxns'][txnID], mainDB, description + ' '):
            if txn['sentQuantity'] != 0 or txn['receivedQuantity'] != 0 or txn['feeQuantity'] != 0:

                if combineRows == False:
                    if txn['type'] != 'Rewards': groupTxnList.append(txn)
                    else: groupTxnList.insert(-1,txn)

                elif combineRows == True:
                    
                    if txn['feeQuantity'] != 0:
                        comboFeeRow['feeQuantity'] = comboFeeRow['feeQuantity'] + txn['feeQuantity']
                        comboFeeRow['feeCurrency'] = 'ALGO'
                        txn['feeQuantity'] = 0
                        txn['feeCurrency'] = ''
                    if txn['sentQuantity'] != 0 or txn['receivedQuantity'] != 0 or txn['feeQuantity'] != 0:    
                        if txn['type'] != 'Rewards': groupTxnList.append(txn)
                        else: groupTxnList.insert(-1,txn)

    if combineRows == True and comboFeeRow['feeQuantity'] != 0:
        groupTxnList.insert(-1,comboFeeRow)

    return groupTxnList

def buildSingleRow(rawTxn, mainDB, description):
    txnTypeDetail = returnTxnTypeInfo()
    txnSpecs = rawTxn[txnTypeDetail[rawTxn['tx-type']][0]]

    singleTxn = returnAssetMovements(rawTxn, txnSpecs, mainDB['wallet'], returnEmptyTxn())

    if 'group' in rawTxn: 
        group = True
        singleTxn['id'] = '(Group- ' + str(rawTxn['group'][:5]) + '...) - ' + rawTxn['id']
    else:
        group = False
        singleTxn['id'] = rawTxn['id']

    if singleTxn['type'] == '': singleTxn['type'] = rawTxn['tx-type']

    if rawTxn['sender'] == mainDB['wallet']:
        singleTxn['type'] = 'Send'
        if group == False: description = description + 'Sender'
        if 'receiver' in txnSpecs:
            singleTxn['txn partner'] = str(txnSpecs['receiver'])
            if txnSpecs['receiver'] in mainDB['addressBook']: singleTxn['txn partner'] = mainDB['addressBook'][txnSpecs['receiver']]['name']
        if rawTxn['fee'] > 0:
            singleTxn['feeCurrency'] = 'ALGO'
            singleTxn['feeQuantity'] = rawTxn['fee']

    elif 'receiver' in txnSpecs and txnSpecs['receiver'] == mainDB['wallet']:
        singleTxn['type'] = 'Receive'
        if rawTxn['sender'] in mainDB['addressBook']: singleTxn['txn partner'] = mainDB['addressBook'][rawTxn['sender']]['name']
        else: singleTxn['txn partner'] = rawTxn['sender']
        if group == False: description = description + 'Receiver'

    if rawTxn['sender'] == mainDB['wallet'] and 'receiver' in txnSpecs and txnSpecs['receiver'] == mainDB['wallet']:
        description = 'Asset Opt in/out'
        singleTxn['type'] = 'Fee'
        singleTxn['txn partner'] = 'Algorand Network'

    innerTxns = returnInnerTxns(rawTxn, mainDB['wallet'], [], rawTxn['id'][:5], description)


    singleTxn['time'] = str(datetime.datetime.fromtimestamp(rawTxn['round-time']))
    singleTxn['description'] = description
    if rawTxn['tx-type'] == 'appl':
        singleTxn['type'] = 'Fee'
        singleTxn['txn partner'] = 'Algorand Network'

    txnList = [singleTxn]


    for innerTxn in innerTxns:
        txnList.append(innerTxn)
  


    rewardsTxn = None
    if rawTxn['sender'] == mainDB['wallet'] and rawTxn['sender-rewards'] != 0:
        rewardsTxn = returnEmptyTxn()
        rewardsTxn['time'] = singleTxn['time']
        rewardsTxn['type'] = 'Rewards'
        rewardsTxn['receivedCurrency'] = 'ALGO'
        rewardsTxn['receivedQuantity'] = rawTxn['sender-rewards']
        if 'group' not in rawTxn:
            rewardsTxn['id'] = 'Sender Rewards - ' + str(rawTxn['id'])
        else:
            rewardsTxn['id'] = '(Group- ' + str(rawTxn['group'][:5]) + '...) - Rewards - ' + str(rawTxn['id'])
        rewardsTxn['description'] = 'Network Participation Rewards'
        rewardsTxn['txn partner'] = 'Algorand Foundation'

    elif 'receiver' in txnSpecs and txnSpecs['receiver'] == mainDB['wallet'] and rawTxn['receiver-rewards'] != 0:
        rewardsTxn = returnEmptyTxn()
        rewardsTxn['time'] = singleTxn['time']
        rewardsTxn['type'] = 'Rewards'
        rewardsTxn['receivedCurrency'] = 'ALGO'
        rewardsTxn['receivedQuantity'] = rawTxn['receiver-rewards']
        if 'group' not in rawTxn:
            rewardsTxn['id'] = 'Receiver Rewards - ' + str(rawTxn['id'])
        else:
            rewardsTxn['id'] = '(Group- ' + str(rawTxn['group'][:5]) + '...) - Rewards - ' + str(rawTxn['id'])    
        rewardsTxn['description'] = 'Network Participation Rewards'
        rewardsTxn['txn partner'] = 'Algorand Foundation'

    if rewardsTxn != None:
        txnList.append(rewardsTxn)


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

