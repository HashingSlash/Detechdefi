import scripts.diagnosisFunctions as diagnosisFunctions

def swapGroup(sellRow, buyRow, feeRowList, platform, comboRow, completeGroupRows):
    processedGroupRows = completeGroupRows
    comboRow['txn partner'] = platform
    comboRow['type'] = 'Swap'
    comboRow['sentQuantity'] = sellRow['sentQuantity']
    comboRow['sentCurrency'] = sellRow['sentCurrency']
    comboRow['receivedQuantity'] = buyRow['receivedQuantity']
    comboRow['receivedCurrency'] = buyRow['receivedCurrency']
    for feeRow in feeRowList:
        comboRow['feeQuantity'] = comboRow['feeQuantity'] + feeRow['sentQuantity']
        processedGroupRows.remove(feeRow)

    processedGroupRows.remove(sellRow)
    processedGroupRows.remove(buyRow)
    processedGroupRows.append(comboRow)

    return processedGroupRows

def addLiquidity(addRowList, poolReceiptRow, feeRowList, platform, comboRow):
    processedGroupRows = []
    comboRow['txn partner'] = platform
    comboRow['type'] = 'Receive LP Tokens'
    for addRow in addRowList:
        addRow['type'] = 'Add Liquidity'
        addRow['txn partner'] = platform
        processedGroupRows.append(addRow)
    if feeRowList != [[]]:
        for feeRow in feeRowList:
            comboRow['feeQuantity'] = comboRow['feeQuantity'] + feeRow['sentQuantity']
    comboRow['receivedQuantity'] = poolReceiptRow['receivedQuantity']
    comboRow['receivedCurrency'] = poolReceiptRow['receivedCurrency']
    processedGroupRows.append(comboRow)
    return processedGroupRows

def removeLiquidity(receiveRowList, poolReceiptRow, feeRowList, platform, comboRow):
    processedGroupRows = []
    comboRow['txn partner'] = platform
    comboRow['type'] = 'Return LP Tokens'
    for receiveRow in receiveRowList:
        receiveRow['type'] = 'Remove Liquidity'
        receiveRow['txn partner'] = platform
        processedGroupRows.append(receiveRow)
    if feeRowList != [[]]:
        for feeRow in feeRowList:
            comboRow['feeQuantity'] = comboRow['feeQuantity'] + feeRow['sentQuantity']
    comboRow['sentQuantity'] = poolReceiptRow['sentQuantity']
    comboRow['sentCurrency'] = poolReceiptRow['sentCurrency']
    processedGroupRows.append(comboRow)
    return processedGroupRows

def claimAssets(receiveRows, feeRows, platform, type, comboRow, groupToProcess):
    processedGroupRows = groupToProcess
    comboRow['txn partner'] = platform
    comboRow['type'] = type
    initComboRow = comboRow

    if feeRows != None:
        for feeTxn in feeRows:
            if feeTxn['sentQuantity'] > 0 and feeTxn['sentCurrency'] == "ALGO":
                comboRow['feeQuantity'] = comboRow['feeQuantity'] + feeTxn['sentQuantity']

    for receiveTxn in receiveRows:
        if receiveTxn['receivedQuantity'] > 0:
            if comboRow['receivedQuantity'] > 0:
                processedGroupRows.append(comboRow)
                comboRow = initComboRow
            comboRow['receivedQuantity'] = receiveTxn['receivedQuantity']
            comboRow['receivedCurrency'] = receiveTxn['receivedCurrency']

    processedGroupRows.append(comboRow)
    return processedGroupRows

def depositAssets(depositRows, feeRows, platform, type, comboRow, groupToProcess):
    processedGroupRows = groupToProcess
    comboRow['txn partner'] = platform
    comboRow['type'] = type
    initComboRow = comboRow

    if feeRows != None:
        for feeTxn in feeRows:
            if feeTxn['sentQuantity'] > 0 and feeTxn['sentCurrency'] == "ALGO":
                comboRow['feeQuantity'] = comboRow['feeQuantity'] + feeTxn['sentQuantity']

    for depositTxn in depositRows:
        if depositTxn['receivedQuantity'] > 0:
            if comboRow['receivedQuantity'] > 0:
                processedGroupRows.append(comboRow)
                comboRow = initComboRow
            comboRow['receivedQuantity'] = depositTxn['receivedQuantity']
            comboRow['receivedCurrency'] = depositTxn['receivedCurrency']


####                This is going to be a mess
#                   Its getting better in here

def specificGroupHandler(groupTxnList, comboRow, groupID):
    removeQue = []
    fastProcess = False
    try:
        firstTxn = groupTxnList[0]
        groupDescription = firstTxn['description']
    except:
        groupDescription = ''
    ####                Fast solve



    ####                single SWAPS
    if len(groupTxnList) > 2 and groupDescription in ['4 txns. Tinyman : Tinyman AMM v1/1.1 : Swap (Buy) ',
                            '4 txns. Tinyman : Tinyman AMM v1/1.1 : Swap (Sell) '] :
        groupTxnList = swapGroup(groupTxnList[1], groupTxnList[2], [groupTxnList[0]], 'Tinyman', comboRow, groupTxnList)
        fastProcess = True
    elif len(groupTxnList) == 2 and groupDescription == '2 txns. Tinyman : Tinyman AMM v2 : Swap (Sell) ':
        groupTxnList = swapGroup(groupTxnList[0], groupTxnList[1], [], 'Tinyman', comboRow, groupTxnList)
        fastProcess = True
    elif groupDescription == '3 txns. Pact : Pact Swap : Swap ':
        groupTxnList = swapGroup(groupTxnList[0], groupTxnList[1], [], 'Pact', comboRow, groupTxnList)
        fastProcess = True
    elif groupDescription == '4 txns. Algofi : AMM : Swap (Buy) ':
        groupTxnList = swapGroup(groupTxnList[0], groupTxnList[1], [], 'AlgoFi', comboRow, groupTxnList)
        fastProcess = True

    ####                Manual Slippage Claims
    elif groupDescription == '3 txns. Tinyman : Tinyman AMM v1/1.1 : Redeem Slippage ':
        groupTxnList = claimAssets(receiveRows=[groupTxnList[1]], feeRows=[groupTxnList[0]], platform='Tinyman', type='Receive',comboRow=comboRow, groupToProcess=[])
        fastProcess = True


    ####                LIQUIDITY
    elif groupDescription == '5 txns. Tinyman : Tinyman AMM v1/1.1 : Add Liquidity ':
        groupTxnList = addLiquidity(addRowList=[groupTxnList[1], groupTxnList[2]],
                                     poolReceiptRow=groupTxnList[3],
                                     feeRowList=[groupTxnList[0]],
                                     platform='Tinyman', comboRow=comboRow)
        fastProcess = True

    elif 'txns. Tinyman : Tinyman AMM v2 : Add ' in groupDescription:
        if len(groupTxnList) ==  2:
            sendList = [groupTxnList[0]]
            receiptRow = groupTxnList[1]
        elif len(groupTxnList) == 3:
            sendList = [groupTxnList[0],groupTxnList[1]]
            receiptRow = groupTxnList[2]
        groupTxnList = addLiquidity(addRowList=sendList,
                                     poolReceiptRow=receiptRow,
                                     feeRowList=[[]],
                                     platform='Tinyman', comboRow=comboRow)
        fastProcess = True

    elif groupDescription == '5 txns. Tinyman : Tinyman AMM v1/1.1 : Remove Liquidity ':
        groupTxnList = removeLiquidity(receiveRowList=[groupTxnList[1], groupTxnList[2]],
                                     poolReceiptRow=groupTxnList[3],
                                     feeRowList=[groupTxnList[0]],
                                     platform='Tinyman', comboRow=comboRow)
        fastProcess = True

    elif groupDescription == '2 txns. Tinyman : Tinyman AMM v2 : Remove Liquidity ':
        if len(groupTxnList) ==  2:
            receiveList = [groupTxnList[1]]
        elif len(groupTxnList) == 3:
            receiveList = [groupTxnList[1],groupTxnList[2]]
        groupTxnList = removeLiquidity(receiveRowList=receiveList,
                                     poolReceiptRow=groupTxnList[0],
                                     feeRowList=[[]],
                                     platform='Tinyman', comboRow=comboRow)
        fastProcess = True


    ####                Claim rewards
    elif groupDescription == '2 txns. Tinyman : Tinyman Staking : Claim ':
        groupTxnList = claimAssets(receiveRows=[groupTxnList[0]], feeRows=None, platform='Tinyman', type='Staking',comboRow=comboRow, groupToProcess=[])
        fastProcess = True








    ####Slow solve    
    if fastProcess == False:
        for txn in groupTxnList:
            if txn == groupTxnList[0]:
                groupDescription = txn['description']
        
        
            ####                Yieldly
            ####                NLL & T3 Staking
            elif groupDescription in ['3 txns. Yieldly : No Loss Lottery : Deposit ', '3 txns. Yieldly : T3 Staking : Deposit ',
                                    '3 txns. Yieldly : T5 Staking : Deposit ', '3 txns. Yieldly : Other Staking : Deposit ']:
                comboRow['type'] = 'Stake'
                comboRow['txn partner'] = 'Yieldly'
                if txn == groupTxnList[0]:
                    comboRow['sentQuantity'] = txn['sentQuantity']
                    comboRow['sentCurrency'] = txn['sentCurrency']
                    removeQue.append(txn)
            elif groupDescription in ['3 txns. Yieldly : T3 Staking : Withdrawal ', '4 txns. Yieldly : T3 Staking : Withdrawal ',
                                    '4 txns. Yieldly : No Loss Lottery : Withdrawal ', '2 txns. Yieldly : T5 Staking : Withdrawal ',
                                    '3 txns. Yieldly : Other Staking : Withdrawal ']:
                comboRow['type'] = 'Unstake'
                comboRow['txn partner'] = 'Yieldly'
                if txn == groupTxnList[0]:
                    comboRow['receivedQuantity'] = txn['receivedQuantity']
                    comboRow['receivedCurrency'] = txn['receivedCurrency']
                    removeQue.append(txn)
                if '4 txns' in groupDescription and txn == groupTxnList[1]:
                    comboRow['feeQuantity'] = comboRow['feeQuantity'] + txn['sentQuantity']
                    removeQue.append(txn)
            elif groupDescription in ['3 txns. Yieldly : T3 Staking : Claim ', '6 txns. Yieldly : T3 Staking : Claim ',
                                    '4 txns. Yieldly : T3 Staking : Close out ', '4 txns. Yieldly : No Loss Lottery : Claim ',
                                    '2 txns. Yieldly : T5 Staking : Claim ', '3 txns. Yieldly : Other Staking : Claim ']:
                comboRow['type'] = 'Reward'
                comboRow['txn partner'] = 'Yieldly'
                if txn == groupTxnList[0]:
                    comboRow['receivedQuantity'] = txn['receivedQuantity']
                    comboRow['receivedCurrency'] = txn['receivedCurrency']
                    removeQue.append(txn)
                elif len(groupTxnList) > 1 and txn == groupTxnList[1]:
                    if groupDescription  == '4 txns. Yieldly : T3 Staking : Close out ':    
                        txn['type'] = 'Unstake'
                    if groupDescription == '4 txns. Yieldly : No Loss Lottery : Claim ' and txn == groupTxnList[1]:
                        comboRow['feeQuantity'] = comboRow['feeQuantity'] + txn['sentQuantity']
                        removeQue.append(txn)
                elif len(groupTxnList) > 2 and txn == groupTxnList[2]:
                    comboRow['feeQuantity'] = comboRow['feeQuantity'] + txn['sentQuantity']
                    removeQue.append(txn)
            elif groupDescription == '2 txns. Yieldly : T5 Staking : Close out ':
                comboRow['txn partner'] = 'Yieldly'





    if removeQue != []:
        for removeTxn in removeQue:
            groupTxnList.remove(removeTxn)

    if comboRow['sentQuantity'] != 0 or comboRow['receivedQuantity'] != 0 or comboRow['feeQuantity'] != 0:
            if comboRow['sentQuantity'] == 0 and comboRow['receivedQuantity'] == 0:
                comboRow['type'] = 'Fee'
                comboRow['id'] = 'Group Combined Fees - ' + groupID
                comboRow['txn partner'] = 'Algorand Network'
            groupTxnList.append(comboRow)



    return groupTxnList
    