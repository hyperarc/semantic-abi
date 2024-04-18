import {DecodedResult, SemanticAbiItem, SemanticAbiItemJson} from "semanticabi/abi/item/semantic/SemanticAbiItem";
import {EthLog} from "semanticabi/metadata/EthLog";
import {EthTrace} from "semanticabi/metadata/EthTrace";
import {SemanticParameters} from "semanticabi/abi/item/semantic/SemanticParameters";
import {SemanticItemProperties} from "semanticabi/abi/item/semantic/SemanticItemProperties";
import {SemanticAbiExecutionError} from "semanticabi/abi/item/semantic/SemanticAbiExecutionError";
import {AbiFunction} from "semanticabi/abi/item/AbiFunction";

/**
 * ABI function decorated with semantics.
 */
export class SemanticAbiFunction extends SemanticAbiItem {

    constructor(
        properties: SemanticItemProperties,
        public readonly inputParameters: SemanticParameters,
        public readonly outputParameters: SemanticParameters,
        public readonly rawItem: AbiFunction
    ) {
        super(properties);
    }

    get allParameters(): SemanticParameters[] {
        return [this.inputParameters, this.outputParameters];
    }

    decode(data: EthLog | EthTrace): DecodedResult {
        if (!(data instanceof EthTrace)) {
            throw new SemanticAbiExecutionError('Can only decode traces.');
        }

        return new DecodedResult(
            data.input.map(i => this.rawItem.decode(i)),
            data.output.map(o => this.rawItem.decodeOutput(o))
        );
    }

    static fromJSON(json: SemanticAbiItemJson): SemanticAbiFunction {
        const rawItem = AbiFunction.fromJSON(json);
        return new SemanticAbiFunction(
            SemanticItemProperties.fromJSON(json),
            SemanticParameters.fromParameters(rawItem.inputs.parameters(), json.inputs),
            SemanticParameters.fromParameters(rawItem.outputs.parameters(), json.outputs),
            rawItem
        );
    }

}
