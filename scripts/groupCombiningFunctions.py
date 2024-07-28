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
    groupLink = ComboRow['link']

    if swapRows != None:
        swapRow = transactionFunctions.returnEmptyTxn()
        swapRow['id'] = 'Swap Row - ' + ComboRow['id']
        swapRow['time'] = ComboRow['time']
        swapRow['description'] = ComboRow['description']
        swapRow['txn partner'] = platform
        swapRow = (swapGroup(swapRows[0], swapRows[1], None, None, platform, swapRow, []))
        processedGroupRows.append(swapRow[0])

    ComboRow['txn partner'] = platform
    ComboRow['type'] = 'Receive LP Tokens'

    for addRow in addRowList:
        addRow['type'] = 'Add Liquidity'
        addRow['txn partner'] = platform
        addRow['link'] = ComboRow['link']
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

    if depositRows != None:
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
    OriginalFolksGroup = None

    groupLink = comboRow['link']

    try:
        firstTxn = groupTxnList[0]
        groupDescription = firstTxn['description']
    except:
        groupDescription = ''
    ####                Fast solve


    ####                Tinyman             ---------------------------------------------------------------------------

    ####                single SWAPS
    if len(groupTxnList) > 2 and groupDescription in ['Tinyman : Tinyman AMM v1/1.1 : Swap (Buy) ',
                                                    'Tinyman : Tinyman AMM v1/1.1 : Swap (Sell) '] :
        groupTxnList = swapGroup(groupTxnList[1], groupTxnList[2], None, [groupTxnList[0]], 'Tinyman', comboRow, groupTxnList)
    elif len(groupTxnList) == 2 and groupDescription == 'Tinyman : Tinyman AMM v2 : Swap (Sell) ':
        groupTxnList = swapGroup(groupTxnList[0], groupTxnList[1], None, [], 'Tinyman', comboRow, groupTxnList)
    elif len(groupTxnList) == 3 and groupDescription == 'Tinyman : Tinyman AMM v2 : Swap (Buy) ':
        groupTxnList = swapGroup(groupTxnList[0], groupTxnList[2], [groupTxnList[1]], [], 'Tinyman', comboRow, groupTxnList)


    ####                Manual Slippage Claims
    elif groupDescription == 'Tinyman : Tinyman AMM v1/1.1 : Redeem Slippage ':
        groupTxnList = claimAssets(receiveRows=[groupTxnList[1]], feeRows=[groupTxnList[0]], platform='Tinyman', type='Receive Slippage',ComboRow=comboRow, groupToProcess=[])


    ####                LIQUIDITY       
    elif groupDescription == 'Tinyman : Tinyman AMM v1/1.1 : Add Liquidity ':
        groupTxnList = addLiquidity(swapRows=None, addRowList=[groupTxnList[1], groupTxnList[2]],
                                     poolReceiptRow=groupTxnList[3],
                                     slippageRows=None,
                                     feeRowList=[groupTxnList[0]],
                                     platform='Tinyman', ComboRow=comboRow)

    elif groupDescription == 'Tinyman : Tinyman AMM v2 : Add Liquidity ':
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

    elif groupDescription == 'Tinyman : Tinyman AMM v1/1.1 : Remove Liquidity ':
        groupTxnList = removeLiquidity(receiveRowList=[groupTxnList[1], groupTxnList[2]],
                                     poolReceiptRow=groupTxnList[3],
                                     slippageRows=None,
                                     feeRowList=[groupTxnList[0]],
                                     platform='Tinyman', ComboRow=comboRow)

    elif groupDescription == 'Tinyman : Tinyman AMM v2 : Remove Liquidity ':
        if len(groupTxnList) ==  2:
            receiveList = [groupTxnList[1]]
        elif len(groupTxnList) == 3:
            receiveList = [groupTxnList[1],groupTxnList[2]]
        groupTxnList = removeLiquidity(receiveRowList=receiveList,
                                     poolReceiptRow=groupTxnList[0],
                                     slippageRows=None,
                                     feeRowList=None,
                                     platform='Tinyman', ComboRow=comboRow)

    ####                Claim rewards
    elif groupDescription == 'Tinyman : Tinyman Staking : Claim ':
        groupTxnList = claimAssets(receiveRows=[groupTxnList[0]], feeRows=None, platform='Tinyman', type='Staking Rewards',ComboRow=comboRow, groupToProcess=[])


    ####                YIELDLY             -------------------------------------------------------------------------------------
    elif groupDescription in ['Yieldly : No Loss Lottery : Deposit ', 'Yieldly : T3 Staking : Deposit ',
                                    'Yieldly : T5 Staking : Deposit ', 'Yieldly : Other Staking : Deposit '] and len(groupTxnList) == 1:
        groupTxnList = depositAssets(depositRows=[groupTxnList[0]], slippageRows=None, feeRows=None, platform="Yieldly", type='Staking Deposit', ComboRow=comboRow, groupToProcess=[])


    elif groupDescription in ['Yieldly : No Loss Lottery : Withdrawal ', 'Yieldly : T3 Staking : Withdrawal ',
                                      'Yieldly : T3 Staking : Withdrawal ',
                                    'Yieldly : T5 Staking : Withdrawal ',
                                    'Yieldly : Other Staking : Withdrawal ']:
        if len(groupTxnList) == 2:
            groupFeeRows = [groupTxnList[1]]
        else: groupFeeRows = None
        groupTxnList = claimAssets(receiveRows=[groupTxnList[0]], feeRows=groupFeeRows, platform='Yieldly', type='Staking Withdrawal',ComboRow=comboRow, groupToProcess=[])

    elif groupDescription in ['Yieldly : No Loss Lottery : Claim ', 'Yieldly : T3 Staking : Claim ',
                              'Yieldly : T5 Staking : Claim ', 'Yieldly : Other Staking : Claim ']:
        groupFeeRows = None
        rewardsRows = [groupTxnList[0]]
        if groupDescription == 'Yieldly : No Loss Lottery : Claim ' and len(groupTxnList) == 2:
            groupFeeRows = [groupTxnList[1]]
        if groupDescription == 'Yieldly : T3 Staking : Claim ' and len(groupTxnList) == 3:
            rewardsRows = [groupTxnList[0], groupTxnList[1]]
            groupFeeRows = [groupTxnList[-1]]
            
        groupTxnList = claimAssets(receiveRows=rewardsRows, feeRows=groupFeeRows, platform='Yieldly', type='Staking Rewards',ComboRow=comboRow, groupToProcess=[])

    elif groupDescription in ['Yieldly : T3 Staking : Close out ']:
        rewardsGroup = claimAssets(receiveRows=[groupTxnList[0]], feeRows=None, platform='Yieldly', type='Staking Rewards',ComboRow=comboRow, groupToProcess=[])
        if len(groupTxnList) > 1:
            unstakeTxn = groupTxnList[1]
            unstakeTxn['type'] = 'Staking Withdrawal'
            unstakeTxn['txn partner'] = 'Yieldly'
            rewardsGroup.append(unstakeTxn)
        groupTxnList = rewardsGroup

    elif groupDescription in ['Yieldly : T5 Staking : Close out ', 'Yieldly : T5 Staking, Other Staking : Close out '] and len(groupTxnList) > 1:
        rewardsGroup = claimAssets(receiveRows=[groupTxnList[1]], feeRows=None, platform='Yieldly', type='Staking Rewards',ComboRow=comboRow, groupToProcess=[])
        if len(groupTxnList) > 1:
            unstakeTxn = groupTxnList[0]
            unstakeTxn['type'] = 'Staking Withdrawal'
            unstakeTxn['txn partner'] = 'Yieldly'
            rewardsGroup.append(unstakeTxn)
        groupTxnList = rewardsGroup



####            Algofund                --------------------------------------------------------------------------------
    elif groupDescription == 'AlgoFund : Staking : Deposit ':
        groupTxnList=depositAssets(depositRows=[groupTxnList[0]],slippageRows=None, feeRows=None,platform='Algofund',
                                   type='Staking Deposit',ComboRow=comboRow, groupToProcess=[])
    elif groupDescription == "AlgoFund : Staking : Claim ":
        groupTxnList = claimAssets(receiveRows=[groupTxnList[1]], feeRows=[groupTxnList[0]],
                                   platform='Algofund', type='Staking Rewards', ComboRow=comboRow, groupToProcess=[])
    elif groupDescription == "AlgoFund : Staking : Withdrawal ":
        groupTxnList = claimAssets(receiveRows=[groupTxnList[1]], feeRows=[groupTxnList[0]],
                                   platform='Algofund', type='Staking Withdrawal', ComboRow=comboRow, groupToProcess=[])



####            Algofi              -----------------------------------------------------------------------------------------

    elif groupDescription in ['Algofi : AMM : Swap (Buy) ',
                              'Algofi : AMM : Swap (Sell) '] and len(groupTxnList) == 2:
        groupTxnList = swapGroup(groupTxnList[0], groupTxnList[1], None, [], 'Algofi', comboRow, groupTxnList)

    elif groupDescription in ['Algofi : AMM : Swap (Buy) '] and len(groupTxnList) == 3:
        groupTxnList = swapGroup(groupTxnList[0], groupTxnList[1], [groupTxnList[2]], [], 'Algofi', comboRow, groupTxnList)

    elif groupDescription in ['Algofi : AMM : Add Liquidity '] and len(groupTxnList) == 3:
        groupTxnList = addLiquidity(swapRows=None, addRowList=[groupTxnList[0], groupTxnList[1]],
                                     poolReceiptRow=groupTxnList[2],
                                     slippageRows=None,
                                     feeRowList=None,
                                     platform='Algofi', ComboRow=comboRow)
    
    elif groupDescription in ['Algofi : AMM : Add Liquidity '] and len(groupTxnList) == 4:
        groupTxnList = addLiquidity(swapRows=None, addRowList=[groupTxnList[0], groupTxnList[1]],
                                     poolReceiptRow=groupTxnList[2],
                                     slippageRows=[groupTxnList[3]],
                                     feeRowList=None,
                                     platform='Algofi', ComboRow=comboRow)
        
    elif groupDescription in ['Algofi : AMM : Swap (Sell), Add Liquidity '] and len(groupTxnList) == 5:
        groupTxnList = addLiquidity(swapRows=[groupTxnList[0], groupTxnList[1]],
                                    addRowList=[groupTxnList[2], groupTxnList[3]],
                                     poolReceiptRow=groupTxnList[4],
                                     slippageRows=None,
                                     feeRowList=None,
                                     platform='Algofi', ComboRow=comboRow)
        
    elif groupDescription in ['Algofi : AMM : Swap (Sell), Add Liquidity '] and len(groupTxnList) == 6:
        groupTxnList = addLiquidity(swapRows=[groupTxnList[0], groupTxnList[1]],
                                    addRowList=[groupTxnList[2], groupTxnList[3]],
                                     poolReceiptRow=groupTxnList[4],
                                     slippageRows=[groupTxnList[5]],
                                     feeRowList=None,
                                     platform='Algofi', ComboRow=comboRow)

    elif groupDescription in ['Algofi : Lending Pool : Swap (Buy), Zap '] and len(groupTxnList) == 6:
        groupTxnList = addLiquidity(swapRows=[groupTxnList[0], groupTxnList[2]],
                                    addRowList=[groupTxnList[3], groupTxnList[4]],
                                     poolReceiptRow=groupTxnList[5],
                                     slippageRows=[groupTxnList[1]],
                                     feeRowList=None,
                                     platform='Algofi', ComboRow=comboRow)


    elif groupDescription in ['Algofi : Lending Pool : Swap (Buy), Zap '] and len(groupTxnList) == 7:
        groupTxnList = addLiquidity(swapRows=[groupTxnList[0],groupTxnList[2]],
                                    addRowList=[groupTxnList[3],groupTxnList[4]],
                                     poolReceiptRow=groupTxnList[5],
                                     slippageRows=[groupTxnList[1], groupTxnList[6]],
                                     feeRowList=None,
                                     platform='Algofi', ComboRow=comboRow)






    elif groupDescription in ['Algofi : AMM : Remove Liquidity '] and len(groupTxnList) == 3:
        groupTxnList = removeLiquidity(receiveRowList=[groupTxnList[1],groupTxnList[2]],
                                     poolReceiptRow=groupTxnList[0],
                                     slippageRows=None,
                                     feeRowList=None,
                                     platform='Algofi', ComboRow=comboRow)
        


    elif groupDescription in['Algofi : Lending Market v2 : Initialize Account ',
                             'Algofi : Algofi Governance : Initialize Account ',
                             'Algofi : Lending Market v1 : Initialize Account ',
                             'Algofi : Staking v1 : Initialize Account ']:
        if len(groupTxnList) == 1:
            groupTxnList = depositAssets(depositRows=[groupTxnList[0]],slippageRows=None, feeRows=None, platform='Algofi - Inital Escrow', type='Deposit', ComboRow=comboRow, groupToProcess=[])

    elif groupDescription in ['Algofi : Lending Market v2 : Add to Collateral ',
                              'Algofi : Lending Market v1 : Mint to Collateral ']:
        if len(groupTxnList) == 1:
            groupTxnList = depositAssets(depositRows=[groupTxnList[0]],slippageRows=None, feeRows=None, platform='Algofi', type='Collateral Deposit', ComboRow=comboRow, groupToProcess=[])

    elif groupDescription in ['Algofi : Lending Market v2 : Remove Collateral ',
                              'Algofi : Lending Market v1 : Remove Collateral ']:
        if len(groupTxnList) == 1:
            groupTxnList = claimAssets(receiveRows=[groupTxnList[0]], feeRows=None, platform='Algofi', type='Collateral Withdrawal', ComboRow=comboRow, groupToProcess=[])

    elif groupDescription in ['Algofi : Lending Market v2 : Borrow ',
                              'Algofi : Lending Market v1 : Borrow ']:
        if len(groupTxnList) == 1:
            groupTxnList = claimAssets(receiveRows=[groupTxnList[0]], feeRows=None, platform='Algofi', type='Borrow', ComboRow=comboRow, groupToProcess=[])

    elif groupDescription in ['Algofi : Lending Market v1 : Repay ']:
        if len(groupTxnList) == 1:
            groupTxnList = depositAssets(depositRows=[groupTxnList[0]],slippageRows=None, feeRows=None, platform='Algofi', type='Repayment', ComboRow=comboRow, groupToProcess=[])
        elif len(groupTxnList) == 2:
            groupTxnList = depositAssets(depositRows=[groupTxnList[1]],slippageRows=[groupTxnList[0]], feeRows=None, platform='Algofi', type='Repayment', ComboRow=comboRow, groupToProcess=[])



    elif groupDescription in ['Algofi : Staking v1 : Claim Rewards ',
                              'Algofi : Staking v2 : Claim Rewards ',
                              'Algofi : Lending Market v1 : Claim Rewards ']:
        if len(groupTxnList) == 1:
            groupTxnList = claimAssets(receiveRows=[groupTxnList[0]], feeRows=None, platform='Algofi', type='Staking Rewards',ComboRow=comboRow, groupToProcess=[])
        if len(groupTxnList) == 2:
            groupTxnList = claimAssets(receiveRows=[groupTxnList[0], groupTxnList[1]], feeRows=None, platform='Algofi', type='Staking Rewards',ComboRow=comboRow, groupToProcess=[])
       
    elif groupDescription in ['Algofi : Staking v1 : Deposit Stake ',
                              'Algofi : Staking v2 : Deposit Stake ']:
        if len(groupTxnList) == 1:
            groupTxnList = depositAssets(depositRows=[groupTxnList[0]],slippageRows=None, feeRows=None, platform='Algofi', type='Staking Deposit', ComboRow=comboRow, groupToProcess=[])



    elif groupDescription in ['Algofi : Staking v1 : Withdraw Stake ']:
        if len(groupTxnList) == 1:
            groupTxnList = claimAssets(receiveRows=[groupTxnList[0]], feeRows=None, platform='Algofi', type='Staking Withdrawal', ComboRow=comboRow, groupToProcess=[])





####                Pact                ---------------------------------------------------------------
    elif groupDescription in ['Pact : Pact Swap : Swap '] and len(groupTxnList) == 2:
        groupTxnList = swapGroup(groupTxnList[0], groupTxnList[1], None, [], 'Pact', comboRow, groupTxnList)


    elif groupDescription in ['Pact : Pact Swap : Add Liquidity '] and len(groupTxnList) == 3:
        groupTxnList = addLiquidity(swapRows=None, addRowList=[groupTxnList[0], groupTxnList[1]],
                                     poolReceiptRow=groupTxnList[2],
                                     slippageRows=None,
                                     feeRowList=None,
                                     platform='Pact', ComboRow=comboRow)
        
    elif groupDescription in ['Pact : Pact Swap : Add Liquidity '] and len(groupTxnList) == 4:
        groupTxnList = addLiquidity(swapRows=None, addRowList=[groupTxnList[0], groupTxnList[1]],
                                     poolReceiptRow=groupTxnList[2],
                                     slippageRows=[groupTxnList[3]],
                                     feeRowList=None,
                                     platform='Pact', ComboRow=comboRow)

    elif groupDescription in ['Pact : Pact Swap : Swap, Add Liquidity '] and len(groupTxnList) == 5:
        groupTxnList = addLiquidity(swapRows=[groupTxnList[0], groupTxnList[1]], addRowList=[groupTxnList[2], groupTxnList[3]],
                                     poolReceiptRow=groupTxnList[4],
                                     slippageRows=None,
                                     feeRowList=None,
                                     platform='Pact', ComboRow=comboRow)

    elif groupDescription in ['Pact : Pact Swap : Swap, Add Liquidity '] and len(groupTxnList) == 6:
        groupTxnList = addLiquidity(swapRows=[groupTxnList[0], groupTxnList[1]], addRowList=[groupTxnList[2], groupTxnList[3]],
                                     poolReceiptRow=groupTxnList[4],
                                     slippageRows=[groupTxnList[5]],
                                     feeRowList=None,
                                     platform='Pact', ComboRow=comboRow)

        
    elif groupDescription in ['Pact : Pact Swap : Remove Liquidity '] and len(groupTxnList) == 3:
        groupTxnList = removeLiquidity(receiveRowList=[groupTxnList[1],groupTxnList[2]],
                                     poolReceiptRow=groupTxnList[0],
                                     slippageRows=None,
                                     feeRowList=None,
                                     platform='Pact', ComboRow=comboRow)
    
    

####                VESTIGE             --------------------------------------------------------------------------------------
    elif len(groupTxnList) == 2 and (' : Swap Aggregator 9225 : Swap' in groupDescription or ': Swap Aggregator 8105 : Swap' in groupDescription):
            groupTxnList = swapGroup(groupTxnList[0], groupTxnList[1], None, None, 'Vestige', comboRow, [])

####                FOLKS               --------------------------------------------------------------------------------------

    elif groupDescription == 'Folks Finance : Swap Aggregator : Swap ' and len(groupTxnList) == 2:
        groupTxnList = swapGroup(groupTxnList[0], groupTxnList[1], None, None, 'Folks Finance', comboRow, [])



    elif groupDescription == 'Folks Finance : Folks Finance v1 : Deposit ' and len(groupTxnList) == 2:
        folksReceiptRow = groupTxnList[0]
        folksReceiptRow['type'] = 'Receive LP Tokens'
        folksReceiptRow['txn partner'] = 'Folks Finance'
        groupTxnList = depositAssets(depositRows=[groupTxnList[1]],slippageRows=None, feeRows=None,
                                     platform='Folks Finance', type='Deposit Collateral', ComboRow=comboRow, groupToProcess=[folksReceiptRow])

    elif groupDescription == 'Folks Finance : Folks Finance v1 : Open Account ' and len(groupTxnList) == 1:
        groupTxnList = depositAssets(depositRows=[groupTxnList[0]],slippageRows=None, feeRows=None, platform='Folks Finance - Initial Escrow', type='Deposit', ComboRow=comboRow, groupToProcess=[])

    elif groupDescription in ['Folks Finance : Folks Finance v1 : Borrow ',
                              'Pact, Folks Finance : Folks Finance v1 : Borrow '] and len(groupTxnList) == 2:
        folksCollateralRow = groupTxnList[1]
        folksCollateralRow['type'] = 'Deposit LP Tokens'
        folksCollateralRow['txn partner'] = 'Folks Finance'
        groupTxnList = claimAssets(receiveRows=[groupTxnList[0]], feeRows=None, platform='Folks Finance', type='Borrow', ComboRow=comboRow, groupToProcess=[folksCollateralRow])

    elif groupDescription in ['Folks Finance : Folks Finance v1 : Increase Borrow ',
                              'Pact, Folks Finance : Folks Finance v1 : Increase Borrow '] and len(groupTxnList) == 1:
        groupTxnList = claimAssets(receiveRows=[groupTxnList[0]], feeRows=None, platform='Folks Finance', type='Borrow', ComboRow=comboRow, groupToProcess=[])

    elif groupDescription == 'Folks Finance : Folks Finance v1 : Withdrawal ' and len(groupTxnList) == 2:
        folksReceiptRow = groupTxnList[1]
        folksReceiptRow['type'] = 'Return LP Tokens'
        folksReceiptRow['txn partner'] = 'Folks Finance'    
        groupTxnList = claimAssets(receiveRows=[groupTxnList[0]], feeRows=None, platform='Folks Finance', type='Withdraw Collateral', ComboRow=comboRow, groupToProcess=[folksReceiptRow])

    elif groupDescription == 'Folks Finance : Folks Finance v1 : Reduce Collateral ' and len(groupTxnList) == 1:
        groupTxnList = claimAssets(receiveRows=[groupTxnList[0]], feeRows=None, platform='Folks Finance', type='Withdraw Collateral', ComboRow=comboRow, groupToProcess=[])


    elif groupDescription == 'Folks Finance : Folks Finance v1 : Lock & Earn ' and len(groupTxnList) == 3:
        folksRewardRow = groupTxnList[1]
        folksRewardRow['type'] = 'Receive LP Tokens'
        folksRewardRow['txn partner'] = 'Folks Finance'
        groupTxnList = depositAssets(depositRows=[groupTxnList[2]],slippageRows=None, feeRows=[groupTxnList[0]], platform='Folks Finance',
                                     type='Staking Deposit', ComboRow=comboRow, groupToProcess=[folksRewardRow])

    elif groupDescription == 'Folks Finance : Folks Finance v1 : Rewards Staking ' and len(groupTxnList) == 2:
        groupTxnList = depositAssets(depositRows=[groupTxnList[1]],slippageRows=None,feeRows=[groupTxnList[0]], platform='Folks Finance',
                                     type='Staking Deposit', ComboRow=comboRow, groupToProcess=[])

    elif groupDescription == 'Folks Finance : Folks Finance v1 : Repay ' and len(groupTxnList) == 4:
        folksRewardRow = groupTxnList[0]
        folksRewardRow['type'] = 'Receive LP Tokens'
        folksRewardRow['txn partner'] = 'Folks Finance'
        folksCollateralRow = groupTxnList[2]
        folksCollateralRow['type'] = 'Withdraw LP Tokens'
        folksCollateralRow['txn partner'] = 'Folks Finance'
        groupTxnList = depositAssets(depositRows=[groupTxnList[3]],slippageRows=[groupTxnList[1]],feeRows=None, platform='Folks Finance',
                                     type='Repayment', ComboRow=comboRow, groupToProcess=[folksRewardRow, folksCollateralRow])

    elif groupDescription == 'Folks Finance : Folks Finance v1 : Repay ' and len(groupTxnList) == 3:
        folksRewardRow = groupTxnList[0]
        folksRewardRow['type'] = 'Receive LP Tokens'
        folksRewardRow['txn partner'] = 'Folks Finance'
        folksCollateralRow = groupTxnList[1]
        folksCollateralRow['type'] = 'Withdraw LP Tokens'
        folksCollateralRow['txn partner'] = 'Folks Finance'
        groupTxnList = depositAssets(depositRows=[groupTxnList[2]],slippageRows=None,feeRows=None, platform='Folks Finance',
                                     type='Repayment', ComboRow=comboRow, groupToProcess=[folksRewardRow, folksCollateralRow])
        
    elif groupDescription == 'Folks Finance : Folks Finance v1 : Repay ' and len(groupTxnList) == 2:
        folksRewardRow = groupTxnList[0]
        folksRewardRow['type'] = 'Receive LP Tokens'
        folksRewardRow['txn partner'] = 'Folks Finance'
        groupTxnList = depositAssets(depositRows=[groupTxnList[1]],slippageRows=None,feeRows=None, platform='Folks Finance',
                                     type='Repayment', ComboRow=comboRow, groupToProcess=[folksRewardRow])

    elif groupDescription == 'Folks Finance : Folks Finance v1 : Rewards Instant ':
        if len(groupTxnList) == 2:
            folksReceiptRow = groupTxnList[1]
            groupTxnList = removeLiquidity(receiveRowList=[groupTxnList[0]], poolReceiptRow=folksReceiptRow, slippageRows=None, feeRowList=None, platform='Folks Finance', ComboRow=comboRow)
        elif len(groupTxnList) == 3:
            folksReceiptRow = groupTxnList[2]
            groupTxnList = removeLiquidity(receiveRowList=[groupTxnList[0], groupTxnList[1]], poolReceiptRow=folksReceiptRow, slippageRows=None, feeRowList=None, platform='Folks Finance', ComboRow=comboRow)
            groupTxnList[1]['type'] = 'Rewards'
        groupTxnList[0]['type'] = 'Rewards'
        



    ####                DEFLEX              ---------------------------------------------------------------
    elif groupDescription == 'Deflex : Swap Aggregator : Swap ' and len(groupTxnList) == 2:
        groupTxnList = swapGroup(groupTxnList[0], groupTxnList[1], None, None, 'Deflex', comboRow, groupTxnList)

    
    elif groupDescription == 'Deflex : Swap Aggregator : Swap ' and len(groupTxnList) == 4:
        groupTxnList = swapGroup(groupTxnList[1], groupTxnList[3], None, [groupTxnList[0], groupTxnList[2]], 'Deflex', comboRow, groupTxnList)











    ####Slow solve    
    if initGroupList == groupTxnList:
        for txn in groupTxnList:
            if txn == groupTxnList[0]:
                txn['link'] = groupLink
                groupDescription = txn['description']

    if comboRow['sentQuantity'] != 0 or comboRow['receivedQuantity'] != 0 or comboRow['feeQuantity'] != 0:
        if comboRow['sentQuantity'] == 0 and comboRow['receivedQuantity'] == 0:
            comboRow['type'] = 'Fee'
            comboRow['id'] = 'Group Combined Fees - ' + groupID
            comboRow['txn partner'] = 'Algorand Network'
            #comboRow['link'] = groupLink
        groupTxnList.append(comboRow)



    return groupTxnList
    