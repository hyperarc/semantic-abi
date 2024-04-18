import {Optional} from "common/Optional";
import {SemanticAbiValidationError} from "semanticabi/abi/item/semantic/SemanticAbiValidateable";
import {DataType} from "semanticabi/transform/column/DataType";

export type ParameterTransformJson = {
    name: string,
    expression?: string,
    type?: string
}

/**
 * Transform for a parameter in an event or function.
 */
export class SemanticParameterTransform {

    constructor(
        public readonly name: Optional<string>,
        public readonly expression: Optional<string>,
        public readonly type: Optional<DataType>
    ) { }

    validate(): Optional<SemanticAbiValidationError> {
        // TODO validate expression
        throw new Error('Not implemented.');
    }

    evaluateExpression(value: any): any {
        return this.expression.map(e => {
            // TODO execute expression
            throw new Error('Not implemented.');
            return null;
        }).getOr(value);
    }

    static fromJSON(json: ParameterTransformJson): SemanticParameterTransform {
        return new SemanticParameterTransform(
            Optional.of(json.name),
            Optional.of(json.expression),
            DataType.fromJSON(json['type'])
        );
    }

}