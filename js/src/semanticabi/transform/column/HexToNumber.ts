import {DatasetColumnTransform} from "semanticabi/transform/column/DatasetColumnTransform";
import {JsonObject} from "common/CommonTypes";
import {Optional} from "common/Optional";

/**
 * Transform a possible hex value to an number. If the value is a string, it will be treated as a hex to be converted,
 * otherwise as an int that does not need conversion.
 *
 * @author zuyezheng
 */
export class HexToNumber implements DatasetColumnTransform {

    constructor(
        public readonly sourceCol: Optional<string> = Optional.none(),

        // specify a (max, default) value pair that if the max is exceeded, will use the default value
        public readonly maxValue: Optional<[number, number]> = Optional.none()
    ) { }

    static convert(v: string | number): number {
        if (typeof v === 'string') {
            return parseInt(v, 16);
        }

        return v;
    }

    transform(blob: JsonObject, key: string): number {
        const value = blob[this.sourceCol.getOr(key)];

        if (value == null) {
            return null;
        }

        const converted = HexToNumber.convert(value);
        return this.maxValue
            .map(([maxV, defaultV]) => converted > maxV ? defaultV : converted)
            .getOr(converted);
    }

}