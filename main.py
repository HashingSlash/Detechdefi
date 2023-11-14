import scripts.databaseFunctions as databaseFunctions
import scripts.diagnosisFunctions as diagnosisFunctions
import scripts.transactionFunctions as transactionFunctions
import scripts.exportFunctions as exportFunctions

print('\nHello')

def main():

    ####                Load/Initialize DBs
    db = databaseFunctions.initMainDB()

    ####                Update database
    node = 'Algonode'
    network = 'Mainnet'


    db = databaseFunctions.fetchTxns(node, network, db)
    db = databaseFunctions.createDatabases(db)

    exportFunctions.saveDB(db)

    exportFunctions.exportDictionaryToCSV(db['apps'], 'resources/appIDs.csv', ['ID','platform','appName'])
    exportFunctions.exportDictionaryToCSV(db['assets'], 'resources/assets.csv', ['ID', 'name', 'unit name', 'decimals'])


    ####                Sort through
    ##testing can be bool or a platform name as a string
    testing = False

    db = diagnosisFunctions.parseGroups(db, testing)
    db['counts'] = databaseFunctions.countMatchedGroups(db['groups'], testing)

    #build rows
    db = transactionFunctions.assembleTransactions(db, testing)

    #export rows via print or file

    exportFunctions.saveDB(db)


    exportFunctions.outputRows('csv', db, '')
    

    #print('Asset prices to find: ' + str(db['prices']['total']))

    print('\nxoxo,\n    Detechdefi\n')
    

main()