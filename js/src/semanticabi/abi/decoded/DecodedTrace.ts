import {DecodedTuple} from "semanticabi/abi/decoded/DecodedTuple";
import {AbiFunction} from "semanticabi/abi/item/AbiFunction";
import {Optional} from "common/Optional";

/**
 * @author zuyezheng
 */
export class DecodedTrace {

    constructor(
        public readonly fn: AbiFunction,
        public readonly input: Optional<DecodedTuple>,
        public readonly output: Optional<DecodedTuple>
    ) {}

}