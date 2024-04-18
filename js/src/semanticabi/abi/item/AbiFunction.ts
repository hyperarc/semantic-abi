import {AbiItem, AbiItemJson} from "semanticabi/abi/item/AbiItem";
import {ItemType} from "semanticabi/abi/item/ItemType";
import {Parameters} from "semanticabi/abi/item/Parameters";
import {DecodedTuple} from "semanticabi/abi/decoded/DecodedTuple";
import {JsonObject} from "common/CommonTypes";
import Web3 from "web3";
import {Optional} from "common/Optional";

/**
 * Parse out a function definition and encapsulate it for decoding.
 *
 * @author zuyezheng
 */
export class AbiFunction extends AbiItem {

    private _hash?: string;

    static fromJSON(itemJson: AbiItemJson): AbiFunction {
        return new AbiFunction(
            itemJson.name,
            ItemType.get(itemJson.type),
            Parameters.fromJSON(itemJson.inputs),
            Parameters.fromJSON(itemJson.outputs),
            itemJson.extra
        );
    }

    constructor(
        name: string,
        public readonly functionType: ItemType,
        inputs: Parameters,
        public readonly outputs: Parameters,
        extra: JsonObject
    ) {
        super(name, inputs, extra);
    }

    get hash(): string {
        if (!this._hash) {
            // functions only use the first 8 hex digits
            this._hash = Web3.utils.soliditySha3(this.signature).slice(2, 10);
        }
        return this._hash;
    }

    decode(input: string): DecodedTuple {
        return DecodedTuple.fromParametersAndValues(
            Optional.none(),
            this.inputs.parameters(),
            AbiItem.WEB3.eth.abi.decodeParameters(
                this.inputs.signatures(),
                input.slice(10)
            )
        );
    }

    decodeOutput(output: string): DecodedTuple {
        return DecodedTuple.fromParametersAndValues(
            Optional.none(),
            this.outputs.parameters(),
            AbiItem.WEB3.eth.abi.decodeParameters(
                this.outputs.signatures(),
                output.slice(2)
            )
        );
    }

}
