import {SemanticAbiValidationError} from "semanticabi/abi/item/semantic/SemanticAbiValidateable";
import {SemanticParameters} from "semanticabi/abi/item/semantic/SemanticParameters";
import {Optional} from "common/Optional";
import {AbiItem} from "semanticabi/abi/item/AbiItem";

export interface SemanticItemTransform {

    /**
     * Validate the config given an array containing at most 2 sets of parameters for the input and output. Return
     * any errors or empty list if none.
     */
    validate(item: AbiItem, inputAndOutputs: SemanticParameters[]): Optional<SemanticAbiValidationError>;

}