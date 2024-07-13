import scripts.diagnosisFunctions as diagnosisFunctions


####                This is going to be a mess

def specificGroupHandler(groupTxnList, comboRow):

    removeQue = []

    for txn in groupTxnList:
        if txn == groupTxnList[0]:
            groupDescription = txn['description']
        ####                Tinyman
        ####                V1/1.1
        if groupDescription in ['4 txns. Tinyman : Tinyman AMM v1/1.1 : Swap (Buy) ', '4 txns. Tinyman : Tinyman AMM v1/1.1 : Swap (Sell) '] :
            ####    Network Fee, Row 1 Sell, Row 1 Buy" 
            comboRow['type'] = 'Trade'
            comboRow['txn partner'] = 'Tinyman'
            if txn == groupTxnList[0]:
                comboRow['feeQuantity'] = comboRow['feeQuantity'] + txn['sentQuantity']
                removeQue.append(txn)
            elif txn == groupTxnList[1]:
                comboRow['sentQuantity'] = txn['sentQuantity']
                comboRow['sentCurrency'] = txn['sentCurrency']
                removeQue.append(txn)
            elif txn == groupTxnList[2]:
                comboRow['receivedQuantity'] = txn['receivedQuantity']
                comboRow['receivedCurrency'] = txn['receivedCurrency']
                removeQue.append(txn)
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
        elif groupDescription == '5 txns. Tinyman : Tinyman AMM v1/1.1 : Add Liquidity ':
            ####       Fee, Deposit, Deposit, get Deposit Receipt.
            comboRow['txn partner'] = 'Tinyman'
            if txn == groupTxnList[0]:
                comboRow['feeQuantity'] = comboRow['feeQuantity'] + txn['sentQuantity']
                removeQue.append(txn)
            elif txn in [groupTxnList[1], groupTxnList[2], groupTxnList[3]]:
                txn['type'] = 'Add Liquidity'
                if txn == groupTxnList[3]:
                    comboRow['receivedQuantity'] = txn['receivedQuantity']
                    comboRow['receivedCurrency'] = txn['receivedCurrency']
                    comboRow['type'] = 'Add Liquidty'
                    removeQue.append(txn)
        elif groupDescription == '5 txns. Tinyman : Tinyman AMM v1/1.1 : Remove Liquidity ':
            ####       Fee, Withdraw, Withdraw, give Deposit Receipt.
            comboRow['txn partner'] = 'Tinyman'
            if txn == groupTxnList[0]:
                comboRow['feeQuantity'] = comboRow['feeQuantity'] + txn['sentQuantity']
                removeQue.append(txn)
            elif txn in [groupTxnList[1], groupTxnList[2], groupTxnList[3]]:
                txn['type'] = 'Remove Liquidity'
                if txn == groupTxnList[3]:
                    comboRow['receivedQuantity'] = txn['receivedQuantity']
                    comboRow['receivedCurrency'] = txn['receivedCurrency']
                    comboRow['type'] = 'Remove Liquidity'
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





    for removeTxn in removeQue:
            groupTxnList.remove(removeTxn)

    comboPack = [groupTxnList, comboRow]
    return comboPack
    