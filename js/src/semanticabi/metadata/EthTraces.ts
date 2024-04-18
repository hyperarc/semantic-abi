import {EthTransactionTraces} from "semanticabi/metadata/EthTransactionTraces";
import {Optional} from "common/Optional";

/**
 * Abstraction for geth and erigon traces.
 *
 * @author zuyezheng
 */
export interface EthTraces {

    /**
     * Get traces for all transactions.
     */
    get transactions(): EthTransactionTraces[]

    /**
     * Get the transactions in the current collection of traces.
     */
    get transactionHashes(): Set<string>

    /**
     * Get possible traces for a specific transaction hash.
     */
    traces(transactionHash: string): Optional<EthTransactionTraces>

}