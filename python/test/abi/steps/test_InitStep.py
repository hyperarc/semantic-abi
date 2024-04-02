import gzip
import json
from typing import List, Dict

from semanticabi.abi.SemanticAbi import SemanticAbi
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EthTransaction import EthTransaction
from semanticabi.metadata.EvmChain import EvmChain
from semanticabi.steps.InitStep import InitStep
from semanticabi.steps.Step import Step


def test_filtered_contract_address():
    with open('test/resources/contracts/seaport/abis/init/contract_address_invalid.json') as file:
        semantic_abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    with gzip.open('test/resources/contracts/seaport/blocks/18937419.json.gz') as file:
        block: EthBlock = EthBlock(EvmChain.ETHEREUM, json.loads(file.read()))

    fulfill_order_transaction: EthTransaction = \
        next(t for t in block.transactions if t.hash == '0xb305d44fd60ea8a92d11c2cd342a850a911ee8a2043c41f0e1ec0507e8e51ace')

    step: Step = InitStep(semantic_abi, semantic_abi.functions_by_hash.get('b3a34c4c'))
    rows: List[Dict[str, any]] = step.transform(block, fulfill_order_transaction)

    # The function should have been filtered out because the contract address is not in the list of contract addresses
    assert len(rows) == 0

def test_valid_contract_address():
    with open('test/resources/contracts/seaport/abis/init/contract_address_valid.json') as file:
        semantic_abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    with gzip.open('test/resources/contracts/seaport/blocks/18937419.json.gz') as file:
        block: EthBlock = EthBlock(EvmChain.ETHEREUM, json.loads(file.read()))

    fulfill_order_transaction: EthTransaction = \
        next(t for t in block.transactions if t.hash == '0xb305d44fd60ea8a92d11c2cd342a850a911ee8a2043c41f0e1ec0507e8e51ace')

    step: Step = InitStep(semantic_abi, semantic_abi.functions_by_hash.get('b3a34c4c'))
    rows: List[Dict[str, any]] = step.transform(block, fulfill_order_transaction)

    # The function should have been accepted
    assert len(rows) == 1
