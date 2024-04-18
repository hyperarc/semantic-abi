import {SemanticAbiItem} from "semanticabi/abi/item/semantic/SemanticAbiItem";
import {SemanticParameter, SemanticParameters} from "semanticabi/abi/item/semantic/SemanticParameters";
import {FlattenedParameter} from "semanticabi/transform/steps/FlattenedParameter";
import {SemanticAbiFunction} from "semanticabi/abi/item/semantic/SemanticAbiFunction";
import {Optional} from "common/Optional";
import {DatasetColumn} from "semanticabi/transform/column/DatasetColumn";

/**
 * Iterates through the parameters of an abi, flattening any tuple components to individual columns, and returning a
 * list of the parameters that can be used to build the schema.
 *
 * For primitive parameters, we just create a column with the parameter name as the column name. For tuple parameters,
 * we recursively go through the components, and create a column for each primitive component with a name that combines
 * the parent parameter name and the individual parameter's name to ensure uniqueness.
 */
export class ParameterFlattener {

    public readonly flattened: FlattenedParameter[];

    constructor(
        private readonly abiItem: SemanticAbiItem,
        private readonly predicate: FlattenPredicate = new FlattenAllPredicate()
    ) {
        this.flattened = ParameterFlattener.buildParameterList(this.abiItem, this.predicate);
    }

    get datasetColumns(): DatasetColumn[] {
        return this.flattened.map(c => c.finalDatasetColumn);
    }

    public static buildParameterList(abiItem: SemanticAbiItem, predicate: FlattenPredicate): FlattenedParameter[] {
        return [
            ...ParameterFlattener.flattenParameters(abiItem.inputParameters, true, predicate),
            ...Optional.ofType(abiItem, SemanticAbiFunction)
                .map(c => ParameterFlattener.flattenParameters(c.outputParameters, false, predicate))
                .getOr([])
        ];
    }

    private static flattenParameters(
        semanticParameters: SemanticParameters,
        isInput: boolean,
        predicate: FlattenPredicate,
        path: SemanticParameter[] = []
    ): FlattenedParameter[] {
        return Array.from(semanticParameters.parameters.values())
            .filter(parameter => !parameter.exclude && predicate.shouldFlatten(parameter, path))
            .flatMap(parameter => ParameterFlattener.flattenParameter(parameter, isInput, predicate, path));
    }

    private static flattenParameter(
        semanticParameter: SemanticParameter,
        isInput: boolean,
        predicate: FlattenPredicate,
        path: SemanticParameter[]
    ): FlattenedParameter[] {
        return semanticParameter.components
            // Recursively flatten the components of a tuple.
            .map(parameters => ParameterFlattener.flattenParameters(parameters, isInput, predicate, path.concat(semanticParameter)))
            // Flatten a single parameter.
            .getOrElse(() => [new FlattenedParameter(
                semanticParameter,
                path,
                ParameterFlattener.buildColumnName(path, semanticParameter.name),
                isInput
            )]);
    }

    private static buildColumnName(path: SemanticParameter[], name: string): string {
        return [...path.map(p => p.name), name].join('_');
    }

}

/**
 * Predicate to determine what parameters to flatten.
 */
export interface FlattenPredicate {

    shouldFlatten(parameter: SemanticParameter, path: SemanticParameter[]): boolean;

}

/**
 * Flattens all non-array parameters.
 */
export class FlattenAllPredicate implements FlattenPredicate {

    shouldFlatten(parameter: SemanticParameter, path: SemanticParameter[]): boolean {
        return !parameter.parameter.isArray;
    }

}