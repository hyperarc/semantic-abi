import { Optional } from "common/Optional";
import {EthTraces} from "semanticabi/metadata/EthTraces";
import {EthTransactionTraces} from "semanticabi/metadata/EthTransactionTraces";
import {EvmChain} from "semanticabi/metadata/EvmChain";
import {ErigonTrace, ErigonTraceJson} from "semanticabi/metadata/ErigonTrace";
import {TraceType} from "semanticabi/metadata/TraceType";
import {JsonObject} from "common/CommonTypes";

/**
 * All Erigon traces for a block.
 *
 * @author zuyezheng
 */
export class ErigonTraces implements EthTraces {

    // traces grouped by transaction and indexed by transaction hash
    public readonly transactionsByHash: Map<string, EthTransactionTraces>;
    // mining rewards
    public readonly rewards: ErigonTrace[];

    constructor(
        public readonly chain: EvmChain,
        public readonly blockNumber: number,
        tracesJson: ErigonTraceJson[]
    ) {
        this.transactionsByHash = new Map();
        this.rewards = [];

        let currentTransaction: EthTransactionTraces = null;
        for (const traceJson of tracesJson) {
            const trace = new ErigonTrace(this.chain, traceJson);
            if (trace.type === TraceType.REWARD) {
                this.rewards.push(trace);
            } else {
                if (currentTransaction == null || currentTransaction.hash !== trace.transactionHash) {
                    // traces are ordered by transaction hash starting with a root, if hash changed, start a new
                    currentTransaction = new EthTransactionTraces(trace);
                    this.transactionsByHash.set(currentTransaction.hash, currentTransaction);
                } else {
                    currentTransaction.addTrace(trace);
                }
            }
        }
    }

    get transactions(): EthTransactionTraces[] {
        return Array.from(this.transactionsByHash.values());
    }

    get transactionHashes(): Set<string> {
        return new Set(this.transactionsByHash.keys());
    }

    traces(transactionHash: string): Optional<EthTransactionTraces> {
        return Optional.of(this.transactionsByHash.get(transactionHash));
    }

    /**
     * From a standalone trace extract vs one extracted together with block and receipt info.
     */
    static fromStandalone(chain: EvmChain, json: JsonObject): ErigonTraces {
        return new ErigonTraces(chain, json.slot, json.traces.result);
    }
    
}