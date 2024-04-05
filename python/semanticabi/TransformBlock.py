import asyncio
import json
import sys
from argparse import ArgumentParser

import pyarrow
from pyarrow.lib import Table

from semanticabi.BlockFetcher import BlockFetcher, NodeType
from semanticabi.SemanticTransformer import SemanticTransformer
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EvmChain import EvmChain


async def fetch_and_transform_block(
    node_url: str,
    node_type: NodeType,
    block_number: int,
    chain: EvmChain,
    abi_path: str
):
    async with BlockFetcher(node_url, node_type) as block_fetcher:
        block_json = await block_fetcher.fetch_block(block_number)

    block: EthBlock = EthBlock(chain, block_json)

    with open(abi_path) as file:
        abi = json.loads(file.read())
    transformer = SemanticTransformer(abi)
    results = transformer.transform(block)

    pyarrow_schema = pyarrow.schema(transformer.metadata)

    table = Table.from_pylist(mapping=results, schema=pyarrow_schema)
    print(table.to_pandas().to_string())


if __name__ == '__main__':
    parser = ArgumentParser('Transforms the transactions in a block with a specified semantic ABI')
    parser.add_argument('--chain', type=str)
    parser.add_argument('--node_url', type=str)
    parser.add_argument('--node_type', type=str, default='geth')
    parser.add_argument('--block', type=int)
    parser.add_argument('--abi_path', type=str)
    args = parser.parse_args()

    asyncio.run(
        fetch_and_transform_block(
            args.node_url,
            NodeType[args.node_type.upper()],
            args.block,
            EvmChain(args.chain),
            args.abi_path
        )
    )
