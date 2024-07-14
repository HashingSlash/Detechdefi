import scripts.diagnosisFunctions as diagnosisFunctions

def swapGroup(sellRow, buyRow, feeRowList, platform, comboRow, completeGroupRows):
    processedGroupRows = completeGroupRows
    comboRow['txn partner'] = platform
    comboRow['type'] = 'Trade'
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
    comboRow['txn partner'] = platform
    comboRow['type'] = 'Add Liquidity'
    for addRow in addRowList:
        addRow['type'] = 'Add Liquidity'
        addRow['txn partner'] = platform
    if feeRowList != [[]]:
        for feeRow in feeRowList:
            comboRow['feeQuantity'] = comboRow['feeQuantity'] + feeRow['sentQuantity']
    comboRow['receivedQuantity'] = poolReceiptRow['receivedQuantity']
    comboRow['receivedCurrency'] = poolReceiptRow['receivedCurrency']

    return [comboRow, addRowList]

def removeLiquidity(receiveRowList, poolReceiptRow, feeRowList, platform, comboRow):
    comboRow['txn partner'] = platform
    comboRow['type'] = 'Remove Liquidity'
    for receiveRow in receiveRowList:
        receiveRow['type'] = 'Remove Liquidity'
        receiveRow['txn partner'] = platform
    if feeRowList != [[]]:
        for feeRow in feeRowList:
            comboRow['feeQuantity'] = comboRow['feeQuantity'] + feeRow['sentQuantity']
    comboRow['sentQuantity'] = poolReceiptRow['sentQuantity']
    comboRow['sentCurrency'] = poolReceiptRow['sentCurrency']

    return [comboRow, receiveRowList]

def claimRewards(rewardsRows, feeRows, platform, type, comboRow, completeGroupRows):
    rowsToReturn = completeGroupRows
    comboRow['txn partner'] = platform
    comboRow['type'] = type
    initComboRow = comboRow

    if feeRows != None:
        for feeTxn in feeRows:
            if feeTxn['sentQuantity'] > 0 and feeTxn['sentCurrency'] == "ALGO":
                comboRow['feeQuantity'] = comboRow['feeQuantity'] + feeTxn['sentQuantity']

    for rewardsTxn in rewardsRows:
        if rewardsTxn['receivedQuantity'] > 0:
            if comboRow['receivedQuantity'] > 0:
                rowsToReturn.append(comboRow)
                comboRow = initComboRow
            comboRow['receivedQuantity'] = rewardsTxn['receivedQuantity']
            comboRow['receivedCurrency'] = rewardsTxn['receivedCurrency']

    rowsToReturn.append(comboRow)
    return rowsToReturn

####                This is going to be a mess

def specificGroupHandler(groupTxnList, comboRow, groupID):
    removeQue = []
    fastProcess = False
    try:
        firstTxn = groupTxnList[0]
        groupDescription = firstTxn['description']
    except:
        groupDescription = ''
    ####                Fast solve
    ####                SWAPS
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

    ####                LIQUIDITY
    elif groupDescription == '5 txns. Tinyman : Tinyman AMM v1/1.1 : Add Liquidity ':
        liqudityCombo = addLiquidity(addRowList=[groupTxnList[1], groupTxnList[2]],
                                     poolReceiptRow=groupTxnList[3],
                                     feeRowList=[groupTxnList[0]],
                                     platform='Tinyman', comboRow=comboRow)
        comboRow = liqudityCombo[0]
        groupTxnList = liqudityCombo[1]
        fastProcess = True

    elif 'txns. Tinyman : Tinyman AMM v2 : Add ' in groupDescription:
        if len(groupTxnList) ==  2:
            sendList = [groupTxnList[0]]
            receiptRow = groupTxnList[1]
        elif len(groupTxnList) == 3:
            sendList = [groupTxnList[0],groupTxnList[1]]
            receiptRow = groupTxnList[2]
        liqudityCombo = addLiquidity(addRowList=sendList,
                                     poolReceiptRow=receiptRow,
                                     feeRowList=[[]],
                                     platform='Tinyman', comboRow=comboRow)
        comboRow = liqudityCombo[0]
        groupTxnList = liqudityCombo[1]
        fastProcess = True

    elif groupDescription == '5 txns. Tinyman : Tinyman AMM v1/1.1 : Remove Liquidity ':
        liqudityCombo = removeLiquidity(receiveRowList=[groupTxnList[1], groupTxnList[2]],
                                     poolReceiptRow=groupTxnList[3],
                                     feeRowList=[groupTxnList[0]],
                                     platform='Tinyman', comboRow=comboRow)
        comboRow = liqudityCombo[0]
        groupTxnList = liqudityCombo[1]
        fastProcess = True

    elif groupDescription == '2 txns. Tinyman : Tinyman AMM v2 : Remove Liquidity ':
        if len(groupTxnList) ==  2:
            receiveList = [groupTxnList[1]]
        elif len(groupTxnList) == 3:
            receiveList = [groupTxnList[1],groupTxnList[2]]
        liqudityCombo = removeLiquidity(receiveRowList=receiveList,
                                     poolReceiptRow=groupTxnList[0],
                                     feeRowList=[[]],
                                     platform='Tinyman', comboRow=comboRow)
        comboRow = liqudityCombo[0]
        groupTxnList = liqudityCombo[1]
        fastProcess = True




    ####                Claim rewards

    elif groupDescription == '2 txns. Tinyman : Tinyman Staking : Claim ':
        groupTxnList = claimRewards(rewardsRows=[groupTxnList[0]], feeRows=None, platform='Tinyman', type='Rewards',comboRow=comboRow, completeGroupRows=[])
        fastProcess = True


    ####Slow solve    
    if fastProcess == False:
        for txn in groupTxnList:
            if txn == groupTxnList[0]:
                groupDescription = txn['description']
            ####                Tinyman
            ####                V1/1.1

            if True == False:
                pass

            elif groupDescription == '3 txns. Tinyman : Tinyman AMM v1/1.1 : Redeem Slippage ':
                ####   Network Fee, Return
                comboRow['type'] = 'Receive'
                comboRow['txn partner'] = 'Tinyman'
                if txn == groupTxnList[0]:
                    comboRow['feeQuantity'] = comboRow['feeQuantity'] + txn['sentQuantity']
                    removeQue.append(txn)
                elif txn == groupTxnList[1]:
                    comboRow['receivedQuantity'] = txn['receivedQuantity']
                    comboRow['receivedCurrency'] = txn['receivedCurrency']
                    removeQue.append(txn)
        
        
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
    