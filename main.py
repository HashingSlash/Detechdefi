import scripts.databaseFunctions as databaseFunctions
import scripts.diagnosisFunctions as diagnosisFunctions
import scripts.transactionFunctions as transactionFunctions
import scripts.exportFunctions as exportFunctions

print('\nHello')

def main():

    ####                Load/Initialize DBs
    #this will either return a fresh database or the database from last use.
    db = databaseFunctions.initMainDB()

    ####                Update database
    node = 'Algonode'
    network = 'Mainnet'
    #fetchTxns returns the main database with all txns in raw format for later processing
    if db['rawTxns'] == {} or input('Update stored transactions? (Y/N): ').upper() == 'Y':
        db = databaseFunctions.fetchTxns(node, network, db)
    #createDatabases returns the main database, using stored txns to fill out some subdictionaries.
    db = databaseFunctions.createDatabases(db)

    #export data at this point
    exportFunctions.saveDB(db)
    exportFunctions.exportDictionaryToCSV(db['apps'], 'resources/appIDs.csv', ['ID','platform','appName'])
    exportFunctions.exportDictionaryToCSV(db['assets'], 'resources/assets.csv', ['ID', 'name', 'unit name', 'decimals'])
    exportFunctions.exportDictionaryToCSV(db['addressBook'], 'resources/addressBook.csv', ['address', 'name', 'usage'])

    ####                Sort through
    ##testing can be bool or a platform name as a string
    testing = False
    #this returns the main database after filling out the txn groups subdictionary.
    db = diagnosisFunctions.parseGroups(db, testing)
    #this returns a dictionary counting up the results of the parsing, and stores it in the mainDB
    #db['counts'] = databaseFunctions.countMatchedGroups(db['groups'], testing)

    #build rows
    #this convert raw txndata into conventional txn spreadsheet rows
    db = transactionFunctions.assembleTransactions(db, testing)

    #save the database with the txn rows in it
    exportFunctions.saveDB(db)

    #this exports the stored txn rows. currently supports 'csv' and 'print'
    exportFunctions.outputRows('csv', db, 'Algofi')
    


    #print('Asset prices to find: ' + str(db['prices']['total']))

    print('\nxoxo,\n    Detechdefi\nPossible thanks to Algonode/Nodely and Vestige APIs.\n')
    

main()