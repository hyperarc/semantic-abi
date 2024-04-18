import {DatasetColumnTransform} from "semanticabi/transform/column/DatasetColumnTransform";
import {Optional} from "common/Optional";
import {JsonObject} from "common/CommonTypes";
import {DataType} from "semanticabi/transform/column/DataType";


export type TransformResult = number | string | string[]

/**
 * @author zuyezheng
 */
export class DatasetColumn {

    constructor(
        public readonly name: string,
        public readonly dataType: DataType,
        private readonly transformFn: Optional<DatasetColumnTransform>
    ) {
    }

    transform(data: JsonObject): TransformResult {
        return this.transformFn
            .map(t => t.transform(data, this.name))
            .getOrElse(() => data[this.name]);
    }

    withName(name: string): DatasetColumn {
        return new DatasetColumn(name, this.dataType, this.transformFn);
    }

}