# Detechdefi
this project aims to create a spreadsheet of an Algorand users activity automatically.
I have written these for personal use and have shared it incase others find the work helpful.
This is a refresh/continuation of my previous project AlgoCSV.
I have written this in Visual Studio Code. Create a python envirnment using the requirements.txt

Results are imperfect and not guaranteed

Current features:
Generic group processing (combines in and out txns into single rows when possible)
Tags Group txns with Platform and Action taken information when possible.
Tags groups that interact with multiple platforms and actions when possible.
Most asset movements into a single csv file (ALGO, ASSET, Inner)
Prebuilt lists of Algorand assets and applications
can fetch recent liquidity pools and assets via Vestige API call.

Current Platforms:
Algofi:
    Lend/Borrow v1 & v2 - Init, Deposit, Withdrawl, Borrow, Repay, Governance Votes, Claim rewards
    Staking v1 & v2 - Init, Deposit, Withdraw, Claim
    Algofi Governance - Init, Algofi Governance, Unlock, Claim.
    AMM - Swap, Add LP, Remove LP
    Lending Pool - Swap, Remove LP, Zap

AlgoFund:
    Staking - Deposit, Withdraw, Claim
    Governance - Vote, Opt In

Deflex:
    Swap Aggregator - Swap

Folks Finance:
    Lend/Borrow - Deposit, Withdraw, Borrow, Repay, Increase Borrow, Reduce Collateral,
    Lock & Earn, Rewards Instant, Rewards Staked, Open Account
    Swap Aggregator - Swap

Pact (incomplete):
    AMM - Swap, Add LP, Remove LP
    Swap Aggregator - Swap
    Lending Pools - Swap
    Farms - Create, Stake LP, Withdraw, Claim

Tinyman:
    AMM v1/v1.1 - Swap, Add LP, Remove LP, Redeem Slippage
    AMM v2 - Swap, Add Initial LP, Add LP, Remove LP
    Tinygear Forge - Mint

Vestige:
    Swap Aggregator - Swap

Yieldly:
    No Loss Lottery - Deposit, Withdraw, Claim
    Staking - Deposit, Claim, Withdraw, Close out