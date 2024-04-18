import {Enum} from "common/Enum";
import {DatasetColumn} from "semanticabi/transform/column/DatasetColumn";
import {Optional} from "common/Optional";
import {HexNormalize} from "semanticabi/transform/column/HexNormalize";

/**
 * Support data types in the JS version of semantic ABI.
 */
export class DataType extends Enum {

    static readonly NUMBER = new this('number');
    static readonly STRING = new this('string');

    column(name: string): DatasetColumn {
        return new DatasetColumn(name, this, Optional.none());
    }

    /**
     * All numbers are double/floats in JS so need to do some mapping.
     */
    static fromJSON(type: string): Optional<DataType> {
        if (type == null) {
            return Optional.none();
        }

        switch (type) {
            case 'int':
            case 'double':
                return Optional.some(DataType.NUMBER);
            default:
                return Optional.some( DataType.STRING);
        }
    }

    static hashColumn(name: string): DatasetColumn {
        return new DatasetColumn(name, DataType.STRING, Optional.some(new HexNormalize()));
    }

}
DataType.finalize();
