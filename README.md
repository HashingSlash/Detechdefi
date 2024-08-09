This project aims to create a spreadsheet of an Algorand users activity automatically.
I have written these for personal use and have shared it incase others find the work helpful.
This is a refresh/continuation of my previous project AlgoCSV.
I have written this in Visual Studio Code. To use, create a python envirnment using the requirements.txt

Results are imperfect and not guaranteed to be correct.
Row colouring in images below was manually added for
demonstration purposes as row formatting is not part of a .csv file.

### Current features:
Collects all available transactions from Nodely/AlgoNode.
Doesn't surface txns that don't effect asset balances.
Labels some transactions types such as network fees, swaps, liquidity mint/burns, staking, claiming rewards, and more.
Creates seperate entries for original Participation rewards (base layer function, could be a part of any transaction during programs active period).
Tags Group txns with Platform and Action taken information when possible.
Tags groups that interact with multiple platforms and actions when possible.
Most asset movements into a single csv file (ALGO, ASSET, Inner)
Prebuilt lists of Algorand assets and applications
Can fetch recent liquidity pools and assets via Vestige API call.  
Some features are 'identified' by matching just the app ID, some identification considers app call data and other transaction information.


### Limitations
Platform functions that do not use application calls on-chain. (Some NFT Marketplaces for example)
Some AMMs currently need each pool to be individually identified in the respective platforms .json file
Some Allo.info group links dont work. Seems to be a lower error rate, and the Lora links seem to work.
Only analyses transactions that are returned by Nodely. With some swap aggregators this will only catch the total input and output. 
    This creates limitations with escrow trades like limit orders and NFT sales.
    Swap aggregators show as a single swap, as the actual trades dont contain the users wallet as senders/receivers/foreign accounts in the trade.
I will probably not be building a webGUI for this. CLI only for now. Algorand supports working in python, so try it out ;)