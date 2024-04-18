import {TupleParameter} from "semanticabi/abi/item/Parameter";
import {Decoded} from "semanticabi/abi/decoded/Decoded";
import {DecodedTuple} from "semanticabi/abi/decoded/DecodedTuple";
import {JsonObject} from "common/CommonTypes";
import {Optional} from "common/Optional";

/**
 * @author zuyezheng
 */
export class DecodedTupleArray implements Decoded {

    constructor(
        public readonly parameter: TupleParameter,
        public readonly values: any[]
    ) {}

    addToJson(jsonObj: JsonObject): JsonObject {
        jsonObj[this.parameter.name] = this.values.map(v =>
            DecodedTuple.fromParametersAndValues(Optional.none(), this.parameter.components, v).toJson()
        );

        return jsonObj;
    }

}