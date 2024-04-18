export type EthLog = {

    address: string,
    topics: string[],
    data: string,
    blockNumber: number | string,
    transactionHash: string,
    transactionIndex: number | string,
    blockHash: string,
    //log index relative to the entire block vs transaction possibly in hex
    logIndex: number | string,
    removed: boolean

}