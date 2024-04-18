import {DatasetColumnTransform} from "semanticabi/transform/column/DatasetColumnTransform";
import {JsonObject} from "common/CommonTypes";
import {Optional} from "common/Optional";

/**
 * Lowercase hex strings.
 *
 * @author zuyezheng
 */
export class HexNormalize implements DatasetColumnTransform {

    constructor(
        public readonly sourceCol: Optional<string> = Optional.none()
    ) { }

    static normalize(hex: string): string {
        if (hex == null) {
            return '';
        }

        return hex.toLowerCase();
    }

    transform(blob: JsonObject, key: string): string | string[] {
        return this.transformValue(blob[this.sourceCol.getOr(key)]);
    }

    transformValue(value: any): string | string[] {
        if (value == null) {
            return null;
        }

        if (Array.isArray(value)) {
            return value.map(HexNormalize.normalize);
        } else {
            return HexNormalize.normalize(value);
        }
    }

}