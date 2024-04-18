import {Decoded} from "semanticabi/abi/decoded/Decoded";
import {Parameter, TupleParameter} from "semanticabi/abi/item/Parameter";
import {Optional} from "common/Optional";
import {DecodedTupleArray} from "semanticabi/abi/decoded/DecodedTupleArray";
import {DecodedPrimitive} from "semanticabi/abi/decoded/DecodedPrimitive";
import {JsonObject} from "common/CommonTypes";

/**
 * @author zuyezheng
 */
export class DecodedTuple implements Decoded {

    constructor(
        private readonly parameter: Optional<TupleParameter>,
        private readonly decoded: Decoded[]
    ) { }

    static fromParametersAndValues(
        rootParameter: Optional<TupleParameter>,
        parameters: Parameter[],
        decodedValues: any | any[]
    ): DecodedTuple {
        // if there is a single parameter for output, values will just be the value
        if (!Array.isArray(decodedValues) && typeof decodedValues !== 'object') {
            decodedValues = [decodedValues];
        }

        const decoded: Decoded[] = [];
        for (let i = 0; i < parameters.length; i++) {
            const parameter = parameters[i];
            const value = decodedValues[i];
            if (parameter instanceof TupleParameter) {
                if (parameter.isArray) {
                    decoded.push(new DecodedTupleArray(parameter, value));
                } else {
                    decoded.push(DecodedTuple.fromParametersAndValues(
                        Optional.some(parameter), parameter.components, value
                    ));
                }
            } else {
                decoded.push(new DecodedPrimitive(parameter, value));
            }
        }

        return new DecodedTuple(rootParameter, decoded);
    }

    addToJson(jsonObj: JsonObject): JsonObject {
        const tupleJson: JsonObject = {};
        this.decoded.forEach(d => d.addToJson(tupleJson));

        return this.parameter
            // add to the given json if there is a parameter name
            .map(p => {
                jsonObj[p.name] = tupleJson;
                return jsonObj;
            })
            // otherwise, it's the root tuple so just return the decoded json
            .getOr(tupleJson);
    }

    toJson(): JsonObject {
        return this.addToJson({});
    }
}