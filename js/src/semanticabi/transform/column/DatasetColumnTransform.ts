import {JsonObject} from "common/CommonTypes";
import {TransformResult} from "semanticabi/transform/column/DatasetColumn";

export interface DatasetColumnTransform {

    transform(blob: JsonObject, key: string): TransformResult;

}