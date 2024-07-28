import json
import csv
import scripts.transactionFunctions as transactionFunctions

def printTxnFormat(txnToPrint, soloPrint):

    print()
    for key in txnToPrint:
        if (txnToPrint[key] != '' and txnToPrint[key] != 0): print(key + ' : ' + str(txnToPrint[key]))


def outputRows(function, mainDB, soloPrint):
    
    roundOrder = list(mainDB['txnRounds'].keys())
    roundOrder.sort()
    fileName = 'detechdefi - ' + mainDB['walletName']
    
    if function == 'csv':
        file = open('output/' + fileName + '.csv', 'w', newline='', encoding='utf-8')
        writer = csv.writer(file)
        header = []
        firstRow = True
        pass

    for txnRound in roundOrder:        
        if mainDB['txnRounds'][txnRound] == {}:
            continue

        for txn in mainDB['txnRounds'][txnRound]:
            txnToOutput = transactionFunctions.convertAssetInfo(mainDB['txnRounds'][txnRound][txn], mainDB['assets'])
            if soloPrint == '' or soloPrint in str(txnToOutput):
                if function == 'print': printTxnFormat(txnToOutput, soloPrint)
                elif function == 'csv':
                    if soloPrint == '' or soloPrint in str(txnToOutput):
                        row = []
                        for key in txnToOutput:
                            if firstRow == True: header.append(key)
                            cell = str(txnToOutput[key])
                            if key in ['sentQuantity', 'receivedQuantity', 'feeQuantity']:
                                row.append(cell.rstrip('0'))
                            else: row.append(cell)
                            
                        if firstRow == True:
                            writer.writerow(header)
                            firstRow = False
                        if row[3] != '' or row[5] != '' or row[7] != '':
                            writer.writerow(row)

    if function == 'csv':
        file.close()
        print('Account activity history exported as csv')


def saveDB(dbToSave):
    dbJson = json.dumps(dbToSave)
    outFile = open('resources/db.json', 'w')
    outFile.write(dbJson)
    outFile.close()
    print('\nSaved database\n')

def exportDictionaryToCSV(dictionatryToExport, fileName, header):

    with open(fileName, 'w', newline='', encoding='utf-8') as csv_file:  
        writer = csv.writer(csv_file)
        writer.writerow(header)

        for key in sorted(dictionatryToExport):
            row = [key]
            for subKey in dictionatryToExport[key]:
                row.append(dictionatryToExport[key][subKey])
            writer.writerow(row)
   

    print('\nDictionary exported to CSV @ :' + fileName)