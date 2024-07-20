import scripts.diagnosisFunctions as diagnosisFunctions

def swapGroup(sellRow, buyRow, slippageRows, feeRowList, platform, ComboRow, completeGroupRows):
    processedGroupRows = completeGroupRows
    ComboRow['txn partner'] = platform
    ComboRow['type'] = 'Swap'
    ComboRow['sentQuantity'] = sellRow['sentQuantity']
    ComboRow['sentCurrency'] = sellRow['sentCurrency']
    ComboRow['receivedQuantity'] = buyRow['receivedQuantity']
    ComboRow['receivedCurrency'] = buyRow['receivedCurrency']
    for feeRow in feeRowList:
        ComboRow['feeQuantity'] = ComboRow['feeQuantity'] + feeRow['sentQuantity']
        processedGroupRows.remove(feeRow)

    if slippageRows != None:
        for slippageRow in slippageRows:
            slippageRow['type'] = 'Receive Slippage'
            processedGroupRows.append(slippageRow)

    processedGroupRows.remove(sellRow)
    processedGroupRows.remove(buyRow)
    processedGroupRows.insert(0, ComboRow)

    return processedGroupRows

def addLiquidity(addRowList, poolReceiptRow, feeRowList, platform, ComboRow):
    processedGroupRows = []
    ComboRow['txn partner'] = platform
    ComboRow['type'] = 'Receive LP Tokens'
    for addRow in addRowList:
        addRow['type'] = 'Add Liquidity'
        addRow['txn partner'] = platform
        processedGroupRows.append(addRow)
    if feeRowList != [[]]:
        for feeRow in feeRowList:
            ComboRow['feeQuantity'] = ComboRow['feeQuantity'] + feeRow['sentQuantity']
    ComboRow['receivedQuantity'] = poolReceiptRow['receivedQuantity']
    ComboRow['receivedCurrency'] = poolReceiptRow['receivedCurrency']
    processedGroupRows.append(ComboRow)
    return processedGroupRows

def removeLiquidity(receiveRowList, poolReceiptRow, feeRowList, platform, ComboRow):
    processedGroupRows = []
    ComboRow['txn partner'] = platform
    ComboRow['type'] = 'Return LP Tokens'
    for receiveRow in receiveRowList:
        receiveRow['type'] = 'Remove Liquidity'
        receiveRow['txn partner'] = platform
        processedGroupRows.append(receiveRow)
    if feeRowList != [[]]:
        for feeRow in feeRowList:
            ComboRow['feeQuantity'] = ComboRow['feeQuantity'] + feeRow['sentQuantity']
    ComboRow['sentQuantity'] = poolReceiptRow['sentQuantity']
    ComboRow['sentCurrency'] = poolReceiptRow['sentCurrency']
    processedGroupRows.append(ComboRow)
    return processedGroupRows

def claimAssets(receiveRows, feeRows, platform, type, ComboRow, groupToProcess):
    processedGroupRows = groupToProcess
    ComboRow['txn partner'] = platform
    ComboRow['type'] = type

    if feeRows != None:
        for feeTxn in feeRows:
            if feeTxn['sentQuantity'] > 0 and feeTxn['sentCurrency'] == "ALGO":
                ComboRow['feeQuantity'] = ComboRow['feeQuantity'] + feeTxn['sentQuantity']

    for receiveTxn in receiveRows:
        if receiveTxn['receivedQuantity'] > 0:
            if ComboRow['receivedQuantity'] > 0:
                receiveTxn['txn partner'] = platform
                receiveTxn['type'] = type
                processedGroupRows.append(receiveTxn)
            else:
                ComboRow['receivedQuantity'] = receiveTxn['receivedQuantity']
                ComboRow['receivedCurrency'] = receiveTxn['receivedCurrency']

    processedGroupRows.append(ComboRow)
    return processedGroupRows

def depositAssets(depositRows, feeRows, platform, type, ComboRow, groupToProcess):
    processedGroupRows = groupToProcess
    ComboRow['txn partner'] = platform
    ComboRow['type'] = type

    if feeRows != None:
        for feeTxn in feeRows:
            if feeTxn['sentQuantity'] > 0 and feeTxn['sentCurrency'] == "ALGO":
                ComboRow['feeQuantity'] = ComboRow['feeQuantity'] + feeTxn['sentQuantity']

    for depositTxn in depositRows:
        if depositTxn['sentQuantity'] > 0:
            if ComboRow['sentQuantity'] > 0:
                depositTxn['txn partner'] = platform
                depositTxn['type'] = type
                processedGroupRows.append(depositTxn)
            else:
                ComboRow['sentQuantity'] = depositTxn['sentQuantity']
                ComboRow['sentCurrency'] = depositTxn['sentCurrency']
    processedGroupRows.append(ComboRow)
    return processedGroupRows


####                This is going to be a mess
#                   Its getting better in here

def specificGroupHandler(groupTxnList, comboRow, groupID):
    initGroupList = groupTxnList
    removeQue = []
    try:
        firstTxn = groupTxnList[0]
        groupDescription = firstTxn['description']
    except:
        groupDescription = ''
    ####                Fast solve



    ####                single SWAPS
    if len(groupTxnList) > 2 and groupDescription in ['4 txns. Tinyman : Tinyman AMM v1/1.1 : Swap (Buy) ',
                            '4 txns. Tinyman : Tinyman AMM v1/1.1 : Swap (Sell) '] :
        groupTxnList = swapGroup(groupTxnList[1], groupTxnList[2], None, [groupTxnList[0]], 'Tinyman', comboRow, groupTxnList)
        #fastProcess = True
    elif len(groupTxnList) == 2 and groupDescription == '2 txns. Tinyman : Tinyman AMM v2 : Swap (Sell) ':
        groupTxnList = swapGroup(groupTxnList[0], groupTxnList[1], None, [], 'Tinyman', comboRow, groupTxnList)
        #fastProcess = True
    elif len(groupTxnList) == 3 and groupDescription == '2 txns. Tinyman : Tinyman AMM v2 : Swap (Buy) ':
        groupTxnList = swapGroup(groupTxnList[0], groupTxnList[2], [groupTxnList[1]], [], 'Tinyman', comboRow, groupTxnList)
    elif groupDescription == '3 txns. Pact : Pact Swap : Swap ':
        groupTxnList = swapGroup(groupTxnList[0], groupTxnList[1], None, [], 'Pact', comboRow, groupTxnList)
        #fastProcess = True
    elif groupDescription == '4 txns. Algofi : AMM : Swap (Buy) ':
        groupTxnList = swapGroup(groupTxnList[0], groupTxnList[1], None, [], 'AlgoFi', comboRow, groupTxnList)
        #fastProcess = True

    ####                Manual Slippage Claims
    elif groupDescription == '3 txns. Tinyman : Tinyman AMM v1/1.1 : Redeem Slippage ':
        groupTxnList = claimAssets(receiveRows=[groupTxnList[1]], feeRows=[groupTxnList[0]], platform='Tinyman', type='Receive Slippage',ComboRow=comboRow, groupToProcess=[])
        #fastProcess = True


    ####                LIQUIDITY
    elif groupDescription == '5 txns. Tinyman : Tinyman AMM v1/1.1 : Add Liquidity ':
        groupTxnList = addLiquidity(addRowList=[groupTxnList[1], groupTxnList[2]],
                                     poolReceiptRow=groupTxnList[3],
                                     feeRowList=[groupTxnList[0]],
                                     platform='Tinyman', ComboRow=comboRow)
        #fastProcess = True

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
                                     platform='Tinyman', ComboRow=comboRow)
        #fastProcess = True

    elif groupDescription == '5 txns. Tinyman : Tinyman AMM v1/1.1 : Remove Liquidity ':
        groupTxnList = removeLiquidity(receiveRowList=[groupTxnList[1], groupTxnList[2]],
                                     poolReceiptRow=groupTxnList[3],
                                     feeRowList=[groupTxnList[0]],
                                     platform='Tinyman', ComboRow=comboRow)
        #fastProcess = True

    elif groupDescription == '2 txns. Tinyman : Tinyman AMM v2 : Remove Liquidity ':
        if len(groupTxnList) ==  2:
            receiveList = [groupTxnList[1]]
        elif len(groupTxnList) == 3:
            receiveList = [groupTxnList[1],groupTxnList[2]]
        groupTxnList = removeLiquidity(receiveRowList=receiveList,
                                     poolReceiptRow=groupTxnList[0],
                                     feeRowList=[[]],
                                     platform='Tinyman', ComboRow=comboRow)
        #fastProcess = True

    ####                Claim rewards
    elif groupDescription == '2 txns. Tinyman : Tinyman Staking : Claim ':
        groupTxnList = claimAssets(receiveRows=[groupTxnList[0]], feeRows=None, platform='Tinyman', type='Staking Rewards',ComboRow=comboRow, groupToProcess=[])
        #fastProcess = True


    ####                YIELDLY
    elif groupDescription in ['3 txns. Yieldly : No Loss Lottery : Deposit ', '3 txns. Yieldly : T3 Staking : Deposit ',
                                    '3 txns. Yieldly : T5 Staking : Deposit ', '3 txns. Yieldly : Other Staking : Deposit ']:
        groupTxnList = depositAssets(depositRows=[groupTxnList[0]], feeRows=None, platform="Yieldly", type='Staking Deposit', ComboRow=comboRow, groupToProcess=[])
        #fastProcess = True

    elif groupDescription in ['4 txns. Yieldly : No Loss Lottery : Withdrawal ', '3 txns. Yieldly : T3 Staking : Withdrawal ',
                                      '4 txns. Yieldly : T3 Staking : Withdrawal ',
                                    '2 txns. Yieldly : T5 Staking : Withdrawal ',
                                    '3 txns. Yieldly : Other Staking : Withdrawal ']:
        if '4 txns' in groupDescription:
            groupFeeRows = [groupTxnList[1]]
        else: groupFeeRows = None
        groupTxnList = claimAssets(receiveRows=[groupTxnList[0]], feeRows=groupFeeRows, platform='Yieldly', type='Staking Withdrawal',ComboRow=comboRow, groupToProcess=[])
        #fastProcess = True

    elif groupDescription in ['4 txns. Yieldly : No Loss Lottery : Claim ', '3 txns. Yieldly : T3 Staking : Claim ', '6 txns. Yieldly : T3 Staking : Claim ',
                              '2 txns. Yieldly : T5 Staking : Claim ', '3 txns. Yieldly : Other Staking : Claim ']:
        groupFeeRows = None
        if groupDescription == '4 txns. Yieldly : No Loss Lottery : Claim ':
            groupFeeRows = [groupTxnList[1]]
        if groupDescription == '6 txns. Yieldly : T3 Staking : Claim ':
            rewardsRows = [groupTxnList[0], groupTxnList[1]]
            groupFeeRows = [groupTxnList[-1]]
        else:  
            rewardsRows = [groupTxnList[0]]
        groupTxnList = claimAssets(receiveRows=rewardsRows, feeRows=groupFeeRows, platform='Yieldly', type='Staking Rewards',ComboRow=comboRow, groupToProcess=[])
        #fastProcess = True

    elif groupDescription in ['4 txns. Yieldly : T3 Staking : Close out ']:#, '2 txns. Yieldly : T5 Staking : Close out ', '4 txns. Yieldly : T5 Staking, Other Staking : Close out ']:
        rewardsGroup = claimAssets(receiveRows=[groupTxnList[0]], feeRows=None, platform='Yieldly', type='Staking Rewards',ComboRow=comboRow, groupToProcess=[])
        if len(groupTxnList) > 1:
            unstakeTxn = groupTxnList[1]
            unstakeTxn['type'] = 'Staking Withdrawal'
            unstakeTxn['txn partner'] = 'Yieldly'
            rewardsGroup.append(unstakeTxn)
        groupTxnList = rewardsGroup
        #fastProcess = True

    elif groupDescription in ['2 txns. Yieldly : T5 Staking : Close out ', '4 txns. Yieldly : T5 Staking, Other Staking : Close out '] and len(groupTxnList) > 1:
        rewardsGroup = claimAssets(receiveRows=[groupTxnList[1]], feeRows=None, platform='Yieldly', type='Staking Rewards',ComboRow=comboRow, groupToProcess=[])
        if len(groupTxnList) > 1:
            unstakeTxn = groupTxnList[0]
            unstakeTxn['type'] = 'Staking Withdrawal'
            unstakeTxn['txn partner'] = 'Yieldly'
            rewardsGroup.append(unstakeTxn)
        groupTxnList = rewardsGroup
        #fastProcess = True



####            Algofund
    elif groupDescription == '2 txns. AlgoFund : Staking : Deposit ':
        groupTxnList=depositAssets(depositRows=[groupTxnList[0]],feeRows=None,platform='Algofund',
                                   type='Staking Deposit',ComboRow=comboRow, groupToProcess=[])
        #fastProcess = True
    elif groupDescription == "2 txns. AlgoFund : Staking : Claim ":
        groupTxnList = claimAssets(receiveRows=[groupTxnList[1]], feeRows=[groupTxnList[0]],
                                   platform='Algofund', type='Staking Rewards', ComboRow=comboRow, groupToProcess=[])
        #fastProcess = True
    elif groupDescription == "2 txns. AlgoFund : Staking : Withdrawal ":
        groupTxnList = claimAssets(receiveRows=[groupTxnList[1]], feeRows=[groupTxnList[0]],
                                   platform='Algofund', type='Staking Withdrawal', ComboRow=comboRow, groupToProcess=[])
        #fastProcess = True

####            Algofi
    elif groupDescription in['2 txns. Algofi : Lending Market v2 : Initialize Account ',
                             '3 txns. Algofi : Lending Market v2 : Initialize Account ',
                             '5 txns. Algofi : Algofi Governance : Initialize Account ']:
        groupTxnList = depositAssets(depositRows=[groupTxnList[0]],feeRows=None, platform='Algofi - Initialize Escrow', type='Deposit', ComboRow=comboRow, groupToProcess=[])

    elif groupDescription in ['3 txns. Algofi : Lending Market v2 : Add to Collateral ',
                              '2 txns. Algofi : Lending Market v2 : Add to Collateral ']:
        groupTxnList = depositAssets(depositRows=[groupTxnList[0]],feeRows=None, platform='Algofi', type='Collateral Deposit', ComboRow=comboRow, groupToProcess=[])

    elif groupDescription in ['3 txns. Algofi : Lending Market v2 : Remove Collateral ',
                              '1 txns. Algofi : Lending Market v2 : Remove Collateral ']:
        groupTxnList = claimAssets(receiveRows=[groupTxnList[0]],feeRows=None, platform='Algofi', type='Collateral Withdrawal', ComboRow=comboRow, groupToProcess=[])

    elif groupDescription == '3 txns. Algofi : Lending Market v2 : Borrow ':
        groupTxnList = depositAssets(depositRows=[groupTxnList[0]],feeRows=None, platform='Algofi', type='Borrow', ComboRow=comboRow, groupToProcess=[])



    elif groupDescription in ['13 txns. Algofi : Staking v1 : Claim Rewards ',
                              '2 txns. Algofi : Staking v2 : Claim Rewards ']:
        groupTxnList = claimAssets(receiveRows=[groupTxnList[0]], feeRows=None, platform='Tinyman', type='Staking Rewards',ComboRow=comboRow, groupToProcess=[])
       


    ####Slow solve    
    if initGroupList == groupTxnList:
        for txn in groupTxnList:
            if txn == groupTxnList[0]:
                groupDescription = txn['description']
        
        





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
    