import {SemanticItemTransform} from "semanticabi/abi/item/semantic/SemanticItemTransform";
import { SemanticAbiValidationError } from "semanticabi/abi/item/semantic/SemanticAbiValidateable";
import { SemanticParameters } from "semanticabi/abi/item/semantic/SemanticParameters";
import {Optional} from "common/Optional";
import {AbiItem} from "semanticabi/abi/item/AbiItem";


export type ExpressionJson = {
    name: string,
    type: string,
    expression: string
}

export class Expressions implements SemanticItemTransform {

    validate(item: AbiItem, inputAndOutputs: SemanticParameters[]): Optional<SemanticAbiValidationError> {
        return Optional.none();
    }

}