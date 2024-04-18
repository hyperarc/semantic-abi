import {SemanticParameter} from "semanticabi/abi/item/semantic/SemanticParameters";
import {DatasetColumn} from "semanticabi/transform/column/DatasetColumn";
import {PrimitiveParameter} from "semanticabi/abi/item/Parameter";
import {SemanticAbiExecutionError} from "semanticabi/abi/item/semantic/SemanticAbiExecutionError";
import {DataType} from "semanticabi/transform/column/DataType";
import {DecodedResult} from "semanticabi/abi/item/semantic/SemanticAbiItem";
import {JsonObject} from "common/CommonTypes";
import {HexToNumber} from "semanticabi/transform/column/HexToNumber";
import {HexNormalize} from "semanticabi/transform/column/HexNormalize";

/**
 * Helps build a single flattened parameter.
 */
export class FlattenedParameter {

    constructor(
        // The parameter that this flattened parameter represents.
        public readonly semanticParameter: SemanticParameter,
        // The path to the parameter if the parameter is nested within a tuple.
        public readonly path: SemanticParameter[],
        // The name of the column in the dataset for this parameter based on the path to this parameter.
        public readonly rawColumnName: string,
        // If this is an input or output parameter.
        public readonly isInput: boolean
    ) {}

    /**
     * The final column name for this parameter, which is the raw column name if there is no transform, or the transform
     * name if there is a transform
     */
    get finalColumnName(): string {
        return this.semanticParameter.transform
            .flatMap(t => t.name)
            // default to the raw column name unless one is provided in annotations
            .getOr(this.rawColumnName);
    }

    /**
     * The final column type for this parameter, which is the raw column type if there is no transform, or the transform
     * type if there is a transform.
     */
    get finalDatasetColumn(): DatasetColumn {
        return this.semanticParameter.transform
            .flatMap(t => t.type)
            .map(type => type.column(this.finalColumnName))
            .getOrElse(() => this.buildColumn(this.finalColumnName));
    }

    /**
     * Get the decoded and transformed parameter value for this flattened parameter.
     */
    flattenedValue(decodedResult: DecodedResult): any {
        const fullPath = [...this.path, this.semanticParameter];
        const value = FlattenedParameter.navigatePath(
            fullPath,
            this.isInput ?
                decodedResult.inputs.map(i => i.toJson()).nullable :
                decodedResult.outputs.map(o => o.toJson()).nullable
        );

        return this.applyTransforms(value);
    }

    /**
     * Get the decoded and transformed array values for this flattened parameter.
     */
    flattenedArray(decodedResult: DecodedResult): any[] {
        const fullPath = [...this.path, this.semanticParameter];
        const value = FlattenedParameter.navigateArrayPath(
            fullPath,
            this.isInput ?
                decodedResult.inputs.map(i => i.toJson()).nullable :
                decodedResult.outputs.map(o => o.toJson()).nullable
        );

        return value.map(v => this.applyTransforms(v));
    }

    buildColumn(columnName: string): DatasetColumn {
        const parameter = this.semanticParameter.parameter;
        if (!(parameter instanceof PrimitiveParameter)) {
            throw new SemanticAbiExecutionError('Can only build column type for primitive parameter.');
        }

        // base type given the signature such that uint256 and int8[] all become ints.
        const primitiveType = parameter.signature.replace(/\d|\[]/g, '');
        switch (primitiveType) {
            case 'int':
            case 'uint':
                return DataType.NUMBER.column(columnName);
            case 'address':
                return DataType.hashColumn(columnName);
            case 'bool':
            case 'string':
            case 'bytes':
            default:
                // everything else is a string
                return DataType.STRING.column(columnName);
        }
    }

    private applyTransforms(value: any): any {
        const primitiveType: string = this.semanticParameter.parameter.signature;
        if (primitiveType.startsWith('int') || primitiveType.startsWith('uint')) {
            value = HexToNumber.convert(value);
        } else if (primitiveType.startsWith('address')) {
            value = HexNormalize.normalize(value);
        }

        return this.semanticParameter.transform
            // evaluate the transform expression if needed
            .map(t => t.evaluateExpression(value))
            .getOr(value);
    }

    /**
     * Return the value at the nested path.
     */
    private static navigatePath(path: SemanticParameter[], decodedJson: JsonObject): any {
        return path.reduce(
            (json, param) => {
                if (json == null) {
                    throw new SemanticAbiExecutionError(
                        `Could not find value at path: ${path.map(p => p.name).join('.')}.`
                    );
                }

                return json[param.name];
            },
            decodedJson
        );
    }

    /**
     * Explode the values of a path where one of the parameters is an array.
     */
    private static navigateArrayPath(fullPath: SemanticParameter[], decodedJson: JsonObject): any[] {
        // figure out which parameter in the path is an array
        const arrayParamIndex = fullPath.findIndex(param => param.parameter.isArray);
        if (arrayParamIndex === -1) {
            return null;
        }
        // get the array
        const arrayJson = FlattenedParameter.navigatePath(fullPath.slice(0, arrayParamIndex + 1), decodedJson);

        // explode the array of values
        const remainingPath = fullPath.slice(arrayParamIndex + 1);
        return arrayJson.map((value: any) => FlattenedParameter.navigatePath(remainingPath, value));
    }

}