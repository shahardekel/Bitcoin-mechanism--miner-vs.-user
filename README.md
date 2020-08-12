# Bitcoin-mechanism--miner-vs.-user
experiment with the Bitcoin mechanism from 2 sides of the users: first as a miner that will implement an alternative pricing mechanism. Then, as a user that is facing the current pay-your-bid mechanism used by the miners, trying to get your transactions into the blockchain as fast as possible at a minimum cost.

The miner is interested in selling the room in the block for the highest fee.
Each user has one or more transactions, and wants to buy room in the block for these transactions (paying low fees if possible).
all mined blocks enter the chain and stay in it forever (no block is wasted or disposed).
The fee is paid in units called Satoshi (Satoshi is the smallest currency unit in Bitcoin , and there are 100,000,000 Satoshi in 1 BTC). The range of used fees is very large and it can be between 1 and 2000 Satoshi per byte.

The mempool is the set of pending transactions.
The data you are using was collected by an active node in the Bitcoin network during the monthsAugust-November2017. The node "listened" to the transactions flowing through the network and collected for each transaction the following:
- TXID (string): The TXID of a transaction in the memory pool, encoded as hex in RPC byte order. Unique for each TX.
- size (int): The size of the serialized transaction in bytes
- fee (float): The transaction fee paid by the transaction in Satoshi (1e-8 Bitcoin)
- time (int): The time the transaction entered the memory pool, Unix epoch time format
- output (int): The amount of Satoshi (1e-8 Bitcoin) spent to this output. May be 0
- removed (int): he block header time (Unix epoch time) of the block which includes this transaction. Only returned for confirmed transactions.
- min_value (int): The minimal value of this transaction to the user (in satoshi). (for the TX_data file)
_ max_value (int): The maximal value of this transaction to the user (in satoshi). (for the TX_data file)

for example:
"155d22d2553eed00170233939238b0ee5098d5b1ef91d19420ef96899b677bd3": {"output": 11743613, "removed": 1504473541, "fee": 16046.0, "time": 1504472139.99, "size": 225}

Meaning: this TX entered the mempool on time 1504472139. It entered a block 1402 seconds later, on time 1504472139.99. The size of the TX is 225 bytes, and the total fee offered to the miner was 16046 Satoshi (about 75 Satoshi/byte). The TX transferred 11743613 Satoshi (about 0.11 bitcoin) from some wallet to another (we do not know the source and target).

files:
- bitcoin_mempool_data.csv -  the current state of the mempool
- TX_data.csv - a list of transactions that you want to insert to the blockchain
- main.py
- functions.py
