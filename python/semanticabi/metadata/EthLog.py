from typing import List, TypedDict


class EthLog(TypedDict):
    address: str
    topics: List[str]
    data: str
    blockNumber: int
    transactionHash: str
    transactionIndex: int
    blockHash: str
    # log index relative to the entire block vs transaction possibly in hex
    logIndex: int | str
    removed: bool