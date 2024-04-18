import {EthTrace} from "semanticabi/metadata/EthTrace";
import {Optional} from "common/Optional";
import {CallType} from "semanticabi/metadata/CallType";

/**
 * Encapsulate all traces in a single transaction.
 *
 * @author zuyezheng
 */
export class EthTransactionTraces {

    rootTrace: EthTrace;
    subTraces: Map<string, EthTrace>;

    constructor(rootTrace: EthTrace) {
        this.rootTrace = rootTrace;
        this.subTraces = new Map<string, EthTrace>();
    }

    get hash(): string {
        return this.rootTrace.transactionHash;
    }

    get fromAddress(): string {
        return this.rootTrace.fromAddress;
    }

    get toAddress(): string {
        return this.rootTrace.toAddress;
    }

    get traces(): EthTrace[] {
        return [this.rootTrace, ...Array.from(this.subTraces.values())];
    }

    get value(): Optional<number> {
        return this.rootTrace.value;
    }

    get internalTransactions(): EthTrace[] {
        return Array.from(this.subTraces.values())
            .filter(t => t.callType === CallType.CALL && t.value.map(v => v > 0).getOr(false));
    }

    get errors(): Optional<string[]> {
        const collectedErrors: string[] = [];
        this.rootTrace.error.forEach(e => collectedErrors.push(e));
        for (const trace of this.subTraces.values()) {
            trace.error.forEach(e => collectedErrors.push(e));
        }
        return Optional.of(collectedErrors.length === 0 ? null : collectedErrors);
    }

    addTrace(trace: EthTrace): void {
        this.subTraces.set(trace.traceHash, trace);
    }

    traceByAddress(address: number[]): EthTrace {
        if (address.length === 0) {
            return this.rootTrace;
        }
        // EthTrace.hashTraceAddress should be a static method in EthTrace class
        return this.subTraces.get(EthTrace.hashTraceAddress(address));
    }

    callStack(address: number[]): EthTrace[] {
        let curTrace = this.traceByAddress(address);
        const stack: EthTrace[] = [curTrace];

        while (!curTrace.isRoot) {
            curTrace = this.traceByAddress(curTrace.parentTraceAddress);
            stack.push(curTrace);
        }

        return stack.reverse();
    }

}