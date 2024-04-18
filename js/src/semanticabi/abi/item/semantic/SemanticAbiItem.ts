import {Optional} from "common/Optional";
import {
    SemanticAbiItemPropertiesJson,
    SemanticItemProperties
} from "semanticabi/abi/item/semantic/SemanticItemProperties";
import {SemanticParameterJson, SemanticParameters} from "semanticabi/abi/item/semantic/SemanticParameters";
import {AbiItem, AbiItemJson} from "semanticabi/abi/item/AbiItem";
import {DecodedTuple} from "semanticabi/abi/decoded/DecodedTuple";
import {EthTrace} from "semanticabi/metadata/EthTrace";
import {EthLog} from "semanticabi/metadata/EthLog";
import {
    SemanticAbiValidateable,
    SemanticAbiValidationError
} from "semanticabi/abi/item/semantic/SemanticAbiValidateable";

export abstract class SemanticAbiItem implements SemanticAbiValidateable {

    constructor(
        public readonly properties: SemanticItemProperties
    ) { }

    validate(): Optional<SemanticAbiValidationError> {
        return this.properties.validate()
            .orElse(() =>
                [this.properties.explode, this.properties.matches, this.properties.expressions].reduce(
                    (acc, item) => acc.orElse(() => item.flatMap(i => i.validate(this.rawItem, this.allParameters))),
                    Optional.none<SemanticAbiValidationError>()
                )
            )
            .orElse(() => this.properties.validate());
    }

    abstract get rawItem(): AbiItem;

    abstract get inputParameters(): SemanticParameters;

    abstract get allParameters(): SemanticParameters[];

    abstract decode(data: EthLog | EthTrace): DecodedResult;

}

export class DecodedResult {

    constructor(
        public readonly inputs: Optional<DecodedTuple>,
        public readonly outputs: Optional<DecodedTuple>
    ) {}

}

export type SemanticAbiItemJson = AbiItemJson & SemanticAbiItemPropertiesJson & {

    inputs: SemanticParameterJson[],
    outputs?: SemanticParameterJson[]

}