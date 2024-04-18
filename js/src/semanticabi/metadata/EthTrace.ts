import {EthTransferType} from "semanticabi/metadata/EthTransferType";
import {EthTransferable} from "semanticabi/metadata/EthTransferable";
import {TraceType} from "semanticabi/metadata/TraceType";
import {CallType} from "semanticabi/metadata/CallType";
import {Optional} from "common/Optional";

/**
 * Individual trace abstraction.
 *
 * @author zuyezheng
 */
export abstract class EthTrace implements EthTransferable {

    static hashTraceAddress(traceAddress: number[]): string {
        return traceAddress.join('_');
    }

    get transferType(): EthTransferType {
        return EthTransferType.INTERNAL;
    }

    get parentTraceAddress(): number[] {
        if (this.isRoot) {
            throw new Error('No parent for root trace.');
        }
        return this.traceAddress.slice(0, -1);
    }

    abstract get contractAddress(): string;

    abstract get fromAddress(): string;

    abstract get toAddress(): string;

    abstract get value(): Optional<number>;

    abstract get isRoot(): boolean;

    abstract get blockHash(): string;

    abstract get transactionHash(): string;

    abstract get traceAddress(): number[];

    abstract get traceHash(): string;

    abstract get signature(): Optional<string>;

    abstract get error(): Optional<string>;

    abstract get type(): TraceType;

    abstract get callType(): CallType;

    abstract get input(): Optional<string>;

    abstract get output(): Optional<string>;

    abstract get gas(): Optional<number>;

    abstract get gasUsed(): Optional<number>;

}