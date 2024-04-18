import {Parameter} from "semanticabi/abi/item/Parameter";
import {Decoded} from "semanticabi/abi/decoded/Decoded";

export class DecodedPrimitive implements Decoded {

    parameter: Parameter;
    value: any;

    constructor(parameter: Parameter, value: any) {
        this.parameter = parameter;
        this.value = value;
    }

    addToJson(jsonObj: { [key: string]: any }): { [key: string]: any } {
        let value = this.value;

        if (this.parameter.signature.startsWith('bytes')) {
            // strip out 0x for bytes
            if (this.parameter.isArray) {
                value = value.map((v: any) => v.substring(2));
            } else {
                value = value.substring(2);
            }
        } else if (typeof value === 'string') {
            value = this.normalizeHex(value);
        }

        jsonObj[this.parameter.name] = value;
        return jsonObj;
    }

    normalizeHex(value: string): string {
        if (value.startsWith('0x')) {
            return value.toLowerCase();
        }

        return value;
    }

}