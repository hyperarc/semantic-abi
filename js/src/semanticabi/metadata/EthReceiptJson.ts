import {EthLog} from "semanticabi/metadata/EthLog";

export type EthReceiptJson = {

    blockHash: string;
    blockNumber: number;
    contractAddress?: string;
    cumulativeGasUsed: number;
    effectiveGasPrice: number;
    from: string;
    gasUsed: number;
    logs: EthLog[];
    logsBloom: string;
    status: number;
    to: string;
    transactionHash: string;
    transactionIndex: number;
    type: number;
    error?: string;

}