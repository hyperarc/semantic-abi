import {AbiEvent} from "semanticabi/abi/item/AbiEvent";
import {DecodedTuple} from "semanticabi/abi/decoded/DecodedTuple";

/**
 * @author zuyezheng
 */
export class DecodedLog {

    constructor(
        public readonly event: AbiEvent,
        public readonly data: DecodedTuple
    ) {}

}