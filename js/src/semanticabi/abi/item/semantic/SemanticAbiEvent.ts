import {DecodedResult, SemanticAbiItem, SemanticAbiItemJson} from "semanticabi/abi/item/semantic/SemanticAbiItem";
import {EthLog} from "semanticabi/metadata/EthLog";
import {EthTrace} from "semanticabi/metadata/EthTrace";
import {SemanticParameters} from "semanticabi/abi/item/semantic/SemanticParameters";
import {AbiEvent} from "semanticabi/abi/item/AbiEvent";
import {SemanticItemProperties} from "semanticabi/abi/item/semantic/SemanticItemProperties";
import {Optional} from "common/Optional";
import {SemanticAbiExecutionError} from "semanticabi/abi/item/semantic/SemanticAbiExecutionError";

/**
 * ABI event decorated with semantics.
 */
export class SemanticAbiEvent extends SemanticAbiItem {

    constructor(
        properties: SemanticItemProperties,
        public readonly inputParameters: SemanticParameters,
        public readonly rawItem: AbiEvent
    ) {
        super(properties);
    }

    get allParameters(): SemanticParameters[] {
        return [this.inputParameters];
    }

    decode(data: EthLog | EthTrace): DecodedResult {
        if (data instanceof EthTrace) {
            throw new SemanticAbiExecutionError('Can only decode logs.');
        }

        return new DecodedResult(
            this.rawItem.decode(data),
            Optional.none()
        );
    }

    static fromJSON(json: SemanticAbiItemJson): SemanticAbiEvent {
        const rawItem = AbiEvent.fromJSON(json);
        return new SemanticAbiEvent(
            SemanticItemProperties.fromJSON(json),
            SemanticParameters.fromParameters(rawItem.inputs.parameters(), json.inputs),
            rawItem
        );
    }

}
