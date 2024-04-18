import {EthTrace} from "semanticabi/metadata/EthTrace";
import {EvmChain} from "semanticabi/metadata/EvmChain";
import {JsonObject} from "common/CommonTypes";
import {TraceType} from "semanticabi/metadata/TraceType";
import {CallType} from "semanticabi/metadata/CallType";
import {EthMetadataError} from "semanticabi/metadata/EthMetadataError";
import {Optional} from "common/Optional";

/**
 * Implementation of EthTrace for Erigon.
 *
 * @author zuyezheng
 */
export class ErigonTrace extends EthTrace {

    constructor(
        public readonly chain: EvmChain,
        public readonly traceJson: ErigonTraceJson
    ) {
        super();
    }

    /**
     * This is the "token" contract address represented by the trace, not the address of the contract that emitted the
     * trace which will be the to address. This is only valid for internal transfers which will always be in the native
     * token of the chain.
     */
    get contractAddress(): string {
        return this.chain.nativeTokenAddress;
    }

    get traceAddress(): number[] {
        return this.traceJson.traceAddress;
    }

    get traceHash(): string {
        // Implement the logic as in Python
        return EthTrace.hashTraceAddress(this.traceAddress);
    }

    /**
     * Signature for a function trace is the first 8 hex characters, this will include the 0x.
     */
    get signature(): Optional<string> {
        return this.input.map(i => i.substring(0, 10));
    }

    get parentTraceAddress(): number[] {
        if (this.isRoot) {
            throw new EthMetadataError('No parent for root trace.');
        }
        return this.traceAddress.slice(0, -1);
    }

    get error(): Optional<string>  {
        return Optional.of(this.traceJson.error);
    }

    get blockHash(): string {
        return this.traceJson.blockHash;
    }

    get transactionHash(): string {
        return this.traceJson.transactionHash.toLowerCase();
    }

    get isRoot(): boolean {
        return this.traceJson.traceAddress.length === 0;
    }

    get type(): TraceType {
        return TraceType.get(this.traceJson.type);
    }

    get callType(): CallType {
        return CallType.get(this.action.callType);
    }

    get input(): Optional<string> {
        return Optional.of(this.action.input);
    }

    get output(): Optional<string> {
        return this.result('output');
    }

    get fromAddress(): string {
        return this.action.from.toLowerCase();
    }

    get toAddress(): string {
        // use the presence of init to determine if it is a contract creation trace
        if ('init' in this.action) {
            // to address is the contract address in geth, in erigon we have to look elsewhere
            return this.result('address')
                .map(contractAddress => (contractAddress as string).toLowerCase())
                // contract creation failure or something else
                .getOr('0x0000000000000000000000000000000000000000');
        } else {
            return this.action['to'].toLowerCase();
        }
    }

    get value(): Optional<number> {
        return this.actionHexInt('value');
    }

    get gas(): Optional<number> {
        return this.actionHexInt('gas');
    }

    get gasUsed(): Optional<number> {
        return this.result<string>('gasUsed').map(gasUsed => parseInt(gasUsed, 16));
    }

    private get action(): { [key: string]: any } {
        return this.traceJson.action;
    }

    private actionHexInt(key: string): Optional<number> {
        return Optional.of(this.action[key]).map(v => parseInt(v, 16));
    }

    private result<T extends string | number>(key: string): Optional<T> {
        return Optional.of(this.traceJson.result).map(r => r[key] as T);
    }

}

export type ErigonTraceJson = {

    action: JsonObject;
    blockHash: string;
    blockNumber: number;
    subtraces: number;
    traceAddress: number[];
    transactionHash: string;
    transactionPosition: number;
    type: string;
    result: JsonObject;
    error: string;

};