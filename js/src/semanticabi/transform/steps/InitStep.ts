import {TransformItem} from "semanticabi/transform/steps/TransformItem";
import {EthLog} from "semanticabi/metadata/EthLog";
import {DecodedResult, SemanticAbiItem} from "semanticabi/abi/item/semantic/SemanticAbiItem";
import {EthTrace} from "semanticabi/metadata/EthTrace";
import {HexToNumber} from "semanticabi/transform/column/HexToNumber";
import {Step} from "semanticabi/transform/steps/Step";
import {SemanticAbi} from "semanticabi/abi/SemanticAbi";
import {JsonObject} from "common/CommonTypes";
import {EthTransaction} from "semanticabi/metadata/EthTransaction";
import {EthBlock} from "semanticabi/metadata/EthBlock";
import {AbiSchema} from "semanticabi/transform/steps/AbiSchema";
import {SemanticAbiEvent} from "semanticabi/abi/item/semantic/SemanticAbiEvent";


/**
 * A no-op step that gets initialized with the particular ABI item that it'll handle, and filters the logs or traces by
 * the signature of that item, optionally also filtering those by any contract addresses specified in the ABI, adding an
 * empty row for each matching log or trace
 */
export class InitStep extends Step {

    public readonly schema: AbiSchema;

    constructor(
        public readonly abi: SemanticAbi,
        public readonly abiItem: SemanticAbiItem
    ) {
        super();
        this.schema = new AbiSchema([]);
    }

    get shouldTransform(): boolean {
        return true;
    }

    innerTransform(block: EthBlock, transaction: EthTransaction): [TransformItem, JsonObject[]][] {
        const transformItems = (): TransformItem[] => {
            if (this.abiItem instanceof SemanticAbiEvent) {
                const logs: EthLog[] = transaction.logsByTopic.get(this.abiItem.rawItem.hash) ?? [];
                return logs.map(log => new EventTransformItem(log, () => this.abiItem.decode(log)));
            } else {
                const traces: EthTrace[] = transaction.tracesByTopic.get(this.abiItem.rawItem.hash) ?? [];
                return traces.map(trace => new FunctionTransformItem(trace, () => this.abiItem.decode(trace)));
            }
        };

        return transformItems()
            .filter(transformItem => this.abi.shouldConsider(transformItem.contractAddress))
            .map(transformItem => [transformItem, [{}]]);
    }

}

export class EventTransformItem extends TransformItem {

    constructor(
        public readonly event: EthLog,
        decodedResultFn: () => DecodedResult
    ) {
        super(decodedResultFn);
    }

    get contractAddress(): string {
        return this.event.address;
    }

    get internalIndex(): string {
        return HexToNumber.convert(this.event.logIndex).toString();
    }

    get itemType(): string {
        return 'event';
    }
}

export class FunctionTransformItem extends TransformItem {

    constructor(
        public readonly trace: EthTrace,
        decodedResultFn: () => DecodedResult
    ) {
        super(decodedResultFn);
    }

    get contractAddress(): string {
        return this.trace.toAddress;
    }

    get internalIndex(): string {
        return this.trace.traceHash;
    }

    get itemType(): string {
        return 'function';
    }

}