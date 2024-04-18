import {EvmChain} from "semanticabi/metadata/EvmChain";
import {JsonObject} from "common/CommonTypes";
import {ErigonTraceJson} from "semanticabi/metadata/ErigonTrace";
import {EthReceiptJson} from "semanticabi/metadata/EthReceiptJson";
import {EthTransaction} from "semanticabi/metadata/EthTransaction";
import {HexToNumber} from "semanticabi/transform/column/HexToNumber";
import {EthMetadataError} from "semanticabi/metadata/EthMetadataError";
import {EthTraces} from "semanticabi/metadata/EthTraces";
import {ErigonTraces} from "semanticabi/metadata/ErigonTraces";
import {Optional} from "common/Optional";
import {zip} from "common/Collections";

/**
 * Wrapper around a EVM block with merged receipts and traces.
 *
 * @author zuyezheng
 */
export class EthBlock {

    private _transactions: EthTransaction[];

    constructor(
        public readonly chain: EvmChain,
        private readonly blockJson: EthBlockJson
    ) { }

    get block(): BlockInfoJson {
        return this.blockJson.block;
    }

    get number(): number {
        return HexToNumber.convert(this.block.number);
    }

    get timestamp(): number {
        return HexToNumber.convert(this.block.timestamp);
    }

    get hasTraces(): boolean {
        return this.blockJson.traces != null;
    }

    get transactions(): EthTransaction[] {
        if (this._transactions) {
            return this._transactions;
        }

        const traces: EthTraces = Optional.of(this.blockJson.traces)
            .map(traces => {
                if (
                    // empty, put in a dummy wrapper
                    traces.length === 0 ||
                    // only erigon will have fields like 'traceAddress' at the root
                    traces[0].traceAddress != null
                ) {
                    return new ErigonTraces(this.chain, this.number, this.blockJson.traces);
                } else {
                    throw new EthMetadataError('Geth traces not currently supported in the UI.');
                }
            })
            .nullable;

        this._transactions = zip(this.block.transactions, this.blockJson.receipts)
            .map(([transactionJson, receiptJson]) =>
                new EthTransaction(this.chain, transactionJson, receiptJson, traces.traces(transactionJson.hash))
            );

        return this._transactions;
    }

}

export type EthBlockJson = {

    block: BlockInfoJson,
    receipts: EthReceiptJson[],
    traces: ErigonTraceJson[]

}

export type BlockInfoJson = {

    baseFeePerGas: string;
    difficulty: string;
    extraData: string;
    gasLimit: string;
    gasUsed: string;
    hash: string;
    logsBloom: string;
    miner: string;
    mixHash: string;
    nonce: string;
    number: string;
    parentHash: string;
    receiptsRoot: string;
    sha3Uncles: string;
    size: string;
    stateRoot: string;
    timestamp: string;
    totalDifficulty: string;
    transactionsRoot: string;
    withdrawalsRoot: string;
    transactions: BlockTransactionJson[];
    uncles: string[];
    withdrawals: JsonObject[];

};

export type BlockTransactionJson = {
    
    blockHash: string;
    blockNumber: string;
    from: string;
    gas: string;
    gasPrice: string;
    maxPriorityFeePerGas: string;
    maxFeePerGas: string;
    hash: string;
    input: string;
    nonce: string;
    to: string;
    transactionIndex: string;
    value: string;
    type: string;
    accessList: string;
    chainId: string;

};