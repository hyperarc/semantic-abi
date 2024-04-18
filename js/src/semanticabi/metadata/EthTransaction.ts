import { Optional } from "common/Optional";
import {EthTransferable} from "semanticabi/metadata/EthTransferable";
import {EthTransferType} from "semanticabi/metadata/EthTransferType";
import {EvmChain} from "semanticabi/metadata/EvmChain";
import {EthTransactionTraces} from "semanticabi/metadata/EthTransactionTraces";
import {EthReceiptJson} from "semanticabi/metadata/EthReceiptJson";
import {HexToNumber} from "semanticabi/transform/column/HexToNumber";
import {EthLog} from "semanticabi/metadata/EthLog";
import {TokenTransferDecoded} from "semanticabi/metadata/TokenTransferDecoded";
import {Abi} from "semanticabi/abi/Abi";
import TransfersAbiJson from "semanticabi/abis/TransfersAbi.json";
import {EthTrace} from "semanticabi/metadata/EthTrace";

/**
 * Encapsulate a single EVM transaction.
 */
export class EthTransaction implements EthTransferable {

    private static readonly TRANSFER_ABI = new Abi('Transfer', TransfersAbiJson);

    public readonly transfers: TokenTransferDecoded[] = [];
    public readonly logsByTopic: Map<string, EthLog[]>;
    public readonly tracesByTopic: Map<string, EthTrace[]>;

    constructor(
        public readonly chain: EvmChain,
        public readonly raw: EthTransactionJson,
        public readonly receipt: EthReceiptJson,
        public readonly traces: Optional<EthTransactionTraces>
    ) {
        this.transfers = EthTransaction.decodeTransfers(this.logs);
        this.logsByTopic = EthTransaction.logsByTopic(this.logs);
        this.tracesByTopic = this.traces.map(t => EthTransaction.tracesByTopic(t))
            .getOr(new Map<string, EthTrace[]>());
    }

    /**
     * Contract address of what was transferred. Since the base coin will be transferred in transactions vs tokens in
     * logs, we always return the native token address.
     *
     * This is not to be confused with the contract address field which will be the address of a contracted created in
     * this transaction
     */
    get contractAddress(): string {
        return this.chain.nativeTokenAddress;
    }
    get fromAddress(): string {
        return this.raw['from'].toLowerCase();
    }
    get toAddress(): string {
        return this.raw['to'].toLowerCase();
    }
    get value(): Optional<number> {
        return Optional.of(this.raw['value']).map(HexToNumber.convert);
    }
    get transferType(): EthTransferType {
        return EthTransferType.PRIMARY;
    }

    get hash(): string {
        return this.raw['hash'].toLowerCase();
    }

    get statusEnum(): string {
        return this.receipt['status'] === 0 ? 'error': 'success';
    }

    get isContractCreation(): boolean {
        return this.receipt['contractAddress'] !== null;
    }

    get logs(): EthLog[] {
        return this.receipt['logs'];
    }

    private static decodeTransfers(logs: EthLog[]): TokenTransferDecoded[] {
        return logs.flatMap((log, logI) => TokenTransferDecoded.tryDecode(
            EthTransaction.TRANSFER_ABI, log, logI
        ));
    }

    private static logsByTopic(logs: EthLog[]): Map<string, EthLog[]> {
        return logs.reduce((acc, log) => {
            if (log.topics.length === 0) {
                return acc;
            }

            const topic = log.topics[0].slice(2);
            if (!acc.has(topic)) {
                acc.set(topic, []);
            }
            acc.get(topic).push(log);

            return acc;
        }, new Map<string, EthLog[]>());
    }

    private static tracesByTopic(traces: EthTransactionTraces): Map<string, EthTrace[]> {
        return traces.traces.reduce((acc, trace) => {
            trace.signature
                .map(s => s.slice(2))
                .forEach(s => {
                    if (!acc.has(s)) {
                        acc.set(s, []);
                    }
                    acc.get(s).push(trace);
                });

            return acc;
        }, new Map<string, EthTrace[]>());
    }

}

export type EthTransactionJson = {

    from: string;
    to: string;
    hash: string;
    value?: string | number;

    [key: string]: any

}