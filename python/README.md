# Python implementation
To get started with the python implementation, make sure you have `poetry` installed. Once that's done, you can just do:

```poetry install```

After that, you can try it out with your own semantic abi. You'll need a blockchain node for the chain the block is on so that the block and receipts and traces can be retrieved. To transform the block, you can run:
```shell
python semanticabi/TransformBlock.py --block 1234567 --chain <chain name> --abi_path /path/to/abi.json --node_url <node url> --node_type <geth|erigon>
```
You can find a list of the supported chain names in `semanticabi/metadata/EvmChain.py`. The `node_url` should be the url of the node you're using to retrieve the block data. The `node_type` should be the type of node you're using, either `geth` or `erigon`.