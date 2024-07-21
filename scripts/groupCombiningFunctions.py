import scripts.diagnosisFunctions as diagnosisFunctions
import scripts.transactionFunctions as transactionFunctions

def swapGroup(sellRow, buyRow, slippageRows, feeRowList, platform, ComboRow, completeGroupRows):
    processedGroupRows = []
    ComboRow['txn partner'] = platform
    ComboRow['type'] = 'Swap'
    ComboRow['sentQuantity'] = sellRow['sentQuantity']
    ComboRow['sentCurrency'] = sellRow['sentCurrency']
    ComboRow['receivedQuantity'] = buyRow['receivedQuantity']
    ComboRow['receivedCurrency'] = buyRow['receivedCurrency']
    if feeRowList != None:
        for feeRow in feeRowList:
            ComboRow['feeQuantity'] = ComboRow['feeQuantity'] + feeRow['sentQuantity']
    processedGroupRows.append(ComboRow)
    if slippageRows != None:
        for slippageRow in slippageRows:
            slippageRow['type'] = 'Receive Slippage'
            slippageRow['txn partner'] = platform
            processedGroupRows.append(slippageRow)

    

    return processedGroupRows

def addLiquidity(swapRows, addRowList, poolReceiptRow, slippageRows, feeRowList, platform, ComboRow):
    processedGroupRows = []
    swapRow = None

    if swapRows != None:
        swapRow = transactionFunctions.returnEmptyTxn()
        swapRow['id'] = 'Swap Row - ' + ComboRow['id']
        swapRow['time'] = ComboRow['time']
        swapRow['description'] = ComboRow['description']
        swapRow['txn partner'] = platform
        swapRow = (swapGroup(swapRows[0], swapRows[1], None, None, 'Algofi', swapRow, []))
        processedGroupRows.append(swapRow[0])

    ComboRow['txn partner'] = platform
    ComboRow['type'] = 'Receive LP Tokens'

    for addRow in addRowList:
        addRow['type'] = 'Add Liquidity'
        addRow['txn partner'] = platform
        processedGroupRows.append(addRow)
    if feeRowList != None:
        for feeRow in feeRowList:
            ComboRow['feeQuantity'] = ComboRow['feeQuantity'] + feeRow['sentQuantity']

    ComboRow['receivedQuantity'] = poolReceiptRow['receivedQuantity']
    ComboRow['receivedCurrency'] = poolReceiptRow['receivedCurrency']
    processedGroupRows.append(ComboRow)

    if slippageRows != None:
        for slippageRow in slippageRows:
            slippageRow['txn partner'] = platform
            slippageRow['type'] = 'Receive Slippage'
            processedGroupRows.append(slippageRow)


    return processedGroupRows

def removeLiquidity(receiveRowList, poolReceiptRow, slippageRows, feeRowList, platform, ComboRow):
    processedGroupRows = []
    ComboRow['txn partner'] = platform
    ComboRow['type'] = 'Return LP Tokens'

    for receiveRow in receiveRowList:
        receiveRow['type'] = 'Remove Liquidity'
        receiveRow['txn partner'] = platform
        processedGroupRows.append(receiveRow)
    if feeRowList != None:
        for feeRow in feeRowList:
            ComboRow['feeQuantity'] = ComboRow['feeQuantity'] + feeRow['sentQuantity']
    ComboRow['sentQuantity'] = poolReceiptRow['sentQuantity']
    ComboRow['sentCurrency'] = poolReceiptRow['sentCurrency']
    processedGroupRows.append(ComboRow)
    if slippageRows != None:
        for slippageRow in slippageRows:
            slippageRow['txn partner'] = platform
            slippageRow['type'] = 'Receive Slippage'
            processedGroupRows.append(slippageRow)
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

def depositAssets(depositRows, slippageRows, feeRows, platform, type, ComboRow, groupToProcess):
    processedGroupRows = groupToProcess
    ComboRow['txn partner'] = platform
    ComboRow['type'] = type

    if slippageRows != None:
        for slippageRow in slippageRows:
            slippageRow['txn partner'] = platform
            slippageRow['type'] = 'Receive Slippage'
            processedGroupRows.append(slippageRow)

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


    ####                Tinyman             ---------------------------------------------------------------------------

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


    ####                Manual Slippage Claims
    elif groupDescription == '3 txns. Tinyman : Tinyman AMM v1/1.1 : Redeem Slippage ':
        groupTxnList = claimAssets(receiveRows=[groupTxnList[1]], feeRows=[groupTxnList[0]], platform='Tinyman', type='Receive Slippage',ComboRow=comboRow, groupToProcess=[])
        #fastProcess = True


    ####                LIQUIDITY       
    elif groupDescription == '5 txns. Tinyman : Tinyman AMM v1/1.1 : Add Liquidity ':
        groupTxnList = addLiquidity(swapRows=None, addRowList=[groupTxnList[1], groupTxnList[2]],
                                     poolReceiptRow=groupTxnList[3],
                                     slippageRows=None,
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
        groupTxnList = addLiquidity(swapRows=None, addRowList=sendList,
                                     poolReceiptRow=receiptRow,
                                     slippageRows=None,
                                     feeRowList=None,
                                     platform='Tinyman', ComboRow=comboRow)
        #fastProcess = True

    elif groupDescription == '5 txns. Tinyman : Tinyman AMM v1/1.1 : Remove Liquidity ':
        groupTxnList = removeLiquidity(receiveRowList=[groupTxnList[1], groupTxnList[2]],
                                     poolReceiptRow=groupTxnList[3],
                                     slippageRows=None,
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
                                     slippageRows=None,
                                     feeRowList=None,
                                     platform='Tinyman', ComboRow=comboRow)
        #fastProcess = True

    ####                Claim rewards
    elif groupDescription == '2 txns. Tinyman : Tinyman Staking : Claim ':
        groupTxnList = claimAssets(receiveRows=[groupTxnList[0]], feeRows=None, platform='Tinyman', type='Staking Rewards',ComboRow=comboRow, groupToProcess=[])
        #fastProcess = True


    ####                YIELDLY             -------------------------------------------------------------------------------------
    elif groupDescription in ['3 txns. Yieldly : No Loss Lottery : Deposit ', '3 txns. Yieldly : T3 Staking : Deposit ',
                                    '3 txns. Yieldly : T5 Staking : Deposit ', '3 txns. Yieldly : Other Staking : Deposit ']:
        groupTxnList = depositAssets(depositRows=[groupTxnList[0]], slippageRows=None, feeRows=None, platform="Yieldly", type='Staking Deposit', ComboRow=comboRow, groupToProcess=[])
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



####            Algofund                --------------------------------------------------------------------------------
    elif groupDescription == '2 txns. AlgoFund : Staking : Deposit ':
        groupTxnList=depositAssets(depositRows=[groupTxnList[0]],slippageRows=None, feeRows=None,platform='Algofund',
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



####            Algofi              -----------------------------------------------------------------------------------------

    elif groupDescription in ['4 txns. Algofi : AMM : Swap (Buy) ',
                              '2 txns. Algofi : AMM : Swap (Sell) ',
                              '3 txns. Algofi : AMM : Swap (Sell) '] and len(groupTxnList) == 2:
        groupTxnList = swapGroup(groupTxnList[0], groupTxnList[1], None, [], 'Algofi', comboRow, groupTxnList)

    elif groupDescription in ['3 txns. Algofi : AMM : Swap (Buy) ',
                              '4 txns. Algofi : AMM : Swap (Buy) '] and len(groupTxnList) == 3:
        groupTxnList = swapGroup(groupTxnList[0], groupTxnList[1], [groupTxnList[2]], [], 'Algofi', comboRow, groupTxnList)

    elif groupDescription in ['5 txns. Algofi : AMM : Add Liquidity ',
                              '6 txns. Algofi : AMM : Add Liquidity '] and len(groupTxnList) == 3:
        groupTxnList = addLiquidity(swapRows=None, addRowList=[groupTxnList[0], groupTxnList[1]],
                                     poolReceiptRow=groupTxnList[2],
                                     slippageRows=None,
                                     feeRowList=None,
                                     platform='Algofi', ComboRow=comboRow)
    
    elif groupDescription in ['6 txns. Algofi : AMM : Add Liquidity ',
                              '5 txns. Algofi : AMM : Add Liquidity '] and len(groupTxnList) == 4:
        groupTxnList = addLiquidity(swapRows=None, addRowList=[groupTxnList[0], groupTxnList[1]],
                                     poolReceiptRow=groupTxnList[2],
                                     slippageRows=[groupTxnList[3]],
                                     feeRowList=None,
                                     platform='Algofi', ComboRow=comboRow)
        
    elif groupDescription in ['7 txns. Algofi : AMM : Swap (Sell), Add Liquidity ',
                              '8 txns. Algofi : AMM : Swap (Sell), Add Liquidity '] and len(groupTxnList) == 5:
        groupTxnList = addLiquidity(swapRows=[groupTxnList[0], groupTxnList[1]],
                                    addRowList=[groupTxnList[2], groupTxnList[3]],
                                     poolReceiptRow=groupTxnList[4],
                                     slippageRows=None,
                                     feeRowList=None,
                                     platform='Algofi', ComboRow=comboRow)
        
    elif groupDescription in ['7 txns. Algofi : AMM : Swap (Sell), Add Liquidity ',
                              '8 txns. Algofi : AMM : Swap (Sell), Add Liquidity ',
                              '9 txns. Algofi : AMM : Swap (Sell), Add Liquidity '] and len(groupTxnList) == 6:
        groupTxnList = addLiquidity(swapRows=[groupTxnList[0], groupTxnList[1]],
                                    addRowList=[groupTxnList[2], groupTxnList[3]],
                                     poolReceiptRow=groupTxnList[4],
                                     slippageRows=[groupTxnList[5]],
                                     feeRowList=None,
                                     platform='Algofi', ComboRow=comboRow)



    elif groupDescription in ['3 txns. Algofi : AMM : Remove Liquidity '] and len(groupTxnList) == 3:
        groupTxnList = removeLiquidity(receiveRowList=[groupTxnList[1],groupTxnList[2]],
                                     poolReceiptRow=groupTxnList[0],
                                     slippageRows=None,
                                     feeRowList=None,
                                     platform='Algofi', ComboRow=comboRow)
        


    elif groupDescription in['2 txns. Algofi : Lending Market v2 : Initialize Account ',
                             '3 txns. Algofi : Lending Market v2 : Initialize Account ',
                             '5 txns. Algofi : Algofi Governance : Initialize Account ',
                             '2 txns. Algofi : Lending Market v1 : Initialize Account ',
                             '2 txns. Algofi : Staking v1 : Initialize Account ']:
        if len(groupTxnList) == 1:
            groupTxnList = depositAssets(depositRows=[groupTxnList[0]],slippageRows=None, feeRows=None, platform='Algofi - Initialize Escrow', type='Deposit', ComboRow=comboRow, groupToProcess=[])

    elif groupDescription in ['3 txns. Algofi : Lending Market v2 : Add to Collateral ',
                              '2 txns. Algofi : Lending Market v2 : Add to Collateral ',
                              '15 txns. Algofi : Lending Market v1 : Mint to Collateral ']:
        if len(groupTxnList) == 1:
            groupTxnList = depositAssets(depositRows=[groupTxnList[0]],slippageRows=None, feeRows=None, platform='Algofi', type='Collateral Deposit', ComboRow=comboRow, groupToProcess=[])

    elif groupDescription in ['3 txns. Algofi : Lending Market v2 : Remove Collateral ',
                              '1 txns. Algofi : Lending Market v2 : Remove Collateral ',
                              '14 txns. Algofi : Lending Market v1 : Remove Collateral ']:
        if len(groupTxnList) == 1:
            groupTxnList = claimAssets(receiveRows=[groupTxnList[0]], feeRows=None, platform='Algofi', type='Collateral Withdrawal', ComboRow=comboRow, groupToProcess=[])

    elif groupDescription in ['3 txns. Algofi : Lending Market v2 : Borrow ',
                              '14 txns. Algofi : Lending Market v1 : Borrow ']:
        if len(groupTxnList) == 1:
            groupTxnList = claimAssets(receiveRows=[groupTxnList[0]], feeRows=None, platform='Algofi', type='Borrow', ComboRow=comboRow, groupToProcess=[])

    elif groupDescription in ['15 txns. Algofi : Lending Market v1 : Repay ']:
        if len(groupTxnList) == 1:
            groupTxnList = depositAssets(depositRows=[groupTxnList[0]],slippageRows=None, feeRows=None, platform='Algofi', type='Repayment', ComboRow=comboRow, groupToProcess=[])
        elif len(groupTxnList) == 2:
            groupTxnList = depositAssets(depositRows=[groupTxnList[1]],slippageRows=[groupTxnList[0]], feeRows=None, platform='Algofi', type='Repayment', ComboRow=comboRow, groupToProcess=[])

    elif groupDescription in ['13 txns. Algofi : Staking v1 : Claim Rewards ',
                              '2 txns. Algofi : Staking v2 : Claim Rewards ',
                              '13 txns. Algofi : Lending Market v1 : Claim Rewards ']:
        if len(groupTxnList) == 1:
            groupTxnList = claimAssets(receiveRows=[groupTxnList[0]], feeRows=None, platform='Algofi', type='Staking Rewards',ComboRow=comboRow, groupToProcess=[])
        if len(groupTxnList) == 2:
            groupTxnList = claimAssets(receiveRows=[groupTxnList[0], groupTxnList[1]], feeRows=None, platform='Algofi', type='Staking Rewards',ComboRow=comboRow, groupToProcess=[])
       
    elif groupDescription in ['15 txns. Algofi : Staking v1 : Deposit Stake ']:
        if len(groupTxnList) == 1:
            groupTxnList = depositAssets(depositRows=[groupTxnList[0]],slippageRows=None, feeRows=None, platform='Algofi', type='Staking Deposit', ComboRow=comboRow, groupToProcess=[])

    elif groupDescription in ['14 txns. Algofi : Staking v1 : Withdraw Stake ']:
        if len(groupTxnList) == 1:
            groupTxnList = claimAssets(receiveRows=[groupTxnList[0]], feeRows=None, platform='Algofi', type='Staking Withdrawal', ComboRow=comboRow, groupToProcess=[])





####                Pact                ---------------------------------------------------------------
    elif groupDescription in ['3 txns. Pact : Pact Swap : Swap ',
                              '2 txns. Pact : Pact Swap : Swap '] and len(groupTxnList) == 2:
        groupTxnList = swapGroup(groupTxnList[0], groupTxnList[1], None, [], 'Pact', comboRow, groupTxnList)


    elif groupDescription in ['4 txns. Pact : Pact Swap : Add Liquidity '] and len(groupTxnList) == 3:
        groupTxnList = addLiquidity(swapRows=None, addRowList=[groupTxnList[0], groupTxnList[1]],
                                     poolReceiptRow=groupTxnList[2],
                                     slippageRows=None,
                                     feeRowList=None,
                                     platform='Pact', ComboRow=comboRow)
        
    elif groupDescription in ['4 txns. Pact : Pact Swap : Add Liquidity '] and len(groupTxnList) == 4:
        groupTxnList = addLiquidity(swapRows=None, addRowList=[groupTxnList[0], groupTxnList[1]],
                                     poolReceiptRow=groupTxnList[2],
                                     slippageRows=[groupTxnList[3]],
                                     feeRowList=None,
                                     platform='Pact', ComboRow=comboRow)

    elif groupDescription in ['5 txns. Pact : Pact Swap : Swap, Add Liquidity '] and len(groupTxnList) == 5:
        groupTxnList = addLiquidity(swapRows=[groupTxnList[0], groupTxnList[1]], addRowList=[groupTxnList[2], groupTxnList[3]],
                                     poolReceiptRow=groupTxnList[4],
                                     slippageRows=None,
                                     feeRowList=None,
                                     platform='Pact', ComboRow=comboRow)

    elif groupDescription in ['5 txns. Pact : Pact Swap : Swap, Add Liquidity '] and len(groupTxnList) == 6:
        groupTxnList = addLiquidity(swapRows=[groupTxnList[0], groupTxnList[1]], addRowList=[groupTxnList[2], groupTxnList[3]],
                                     poolReceiptRow=groupTxnList[4],
                                     slippageRows=[groupTxnList[5]],
                                     feeRowList=None,
                                     platform='Pact', ComboRow=comboRow)

        
    elif groupDescription in ['2 txns. Pact : Pact Swap : Remove Liquidity '] and len(groupTxnList) == 3:
        groupTxnList = removeLiquidity(receiveRowList=[groupTxnList[1],groupTxnList[2]],
                                     poolReceiptRow=groupTxnList[0],
                                     slippageRows=None,
                                     feeRowList=None,
                                     platform='Pact', ComboRow=comboRow)
    

        





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
    