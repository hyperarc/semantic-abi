import {FlattenPredicate, ParameterFlattener} from "semanticabi/transform/steps/ParameterFlattener";
import {SemanticParameter} from "semanticabi/abi/item/semantic/SemanticParameters";
import {Step} from "semanticabi/transform/steps/Step";
import {AbiSchema} from "semanticabi/transform/steps/AbiSchema";
import {TransformItem} from "semanticabi/transform/steps/TransformItem";
import {EthTransaction} from "semanticabi/metadata/EthTransaction";
import {EthBlock} from "semanticabi/metadata/EthBlock";
import {SubsequentStep} from "semanticabi/transform/steps/SubsequentStep";
import {SemanticAbiExecutionError} from "semanticabi/abi/item/semantic/SemanticAbiExecutionError";
import {JsonObject} from "common/CommonTypes";
import {zipAll} from "common/Collections";

export class ExplodeFlattenPredicate implements FlattenPredicate {

    constructor(
        public readonly explodePaths: Map<string, string[]>
    ) {}

    /**
     * Only flatten if the parameter's path begins with any of the explode paths.
     */
    shouldFlatten(parameter: SemanticParameter, path: SemanticParameter[]): boolean {
        const fullPath = [...path, parameter];

        // Flatten if the given fullPath matches the criteria of any of the explode paths.
        return Array.from(this.explodePaths.values()).some((explodePathParts) =>
            fullPath.every((pathPart, pathPartI) => {
                if (pathPartI >= explodePathParts.length) {
                    // If the explode path is a subpath of the full path, then it's a component of an exploded tuple,
                    // which we want to include, unless it's another array.
                    return !pathPart.parameter.isArray;
                } else {
                    // Make sure we're still part of the explode path.
                    return pathPart.name === explodePathParts[pathPartI];
                }
            })
        );
    }
}

/**
 * Explodes an array parameter into a row for each element in the array.
 */
export class ExplodeStep extends SubsequentStep {

    public readonly schema: AbiSchema;
    private readonly parameterFlattener: ParameterFlattener;

    constructor(previousStep: Step) {
        super(previousStep);

        const explodePathParts: Map<string, string[]> = this.previousStep.abiItem.properties.explode
            .map(explode => explode.pathParts)
            .getOrElse(() => new Map());
        this.parameterFlattener = new ParameterFlattener(
            this.previousStep.abiItem, new ExplodeFlattenPredicate(explodePathParts)
        );
        this.schema = this.previousStep.schema.withColumns(this.parameterFlattener.datasetColumns);
    }

    get shouldTransform(): boolean {
        return this.abiItem.properties.explode !== null;
    }

    protected innerTransformItem(
        block: EthBlock,
        transaction: EthTransaction,
        item: TransformItem,
        previousData: JsonObject[]
    ): JsonObject[] {
        if (previousData.length === 0) {
            return [];
        }
        if (previousData.length > 1) {
            throw new SemanticAbiExecutionError('Can only explode a single row of data');
        }

        let arrayLength: number = null;
        // Build out the columnar table of data by flattening anything that needs to be flattened.
        const columnarTable: any[][] = this.parameterFlattener.flattened.map((parameter) => {
            const flattenedArray: any[] = parameter.flattenedArray(item.decodedResult);

            if (arrayLength === null) {
                arrayLength = flattenedArray.length;
            } else if (arrayLength !== flattenedArray.length) {
                throw new SemanticAbiExecutionError(`Parameter '${parameter.finalColumnName}' has a different number of elements than the other exploded parameters`);
            }

            return parameter.flattenedArray(item.decodedResult);
        });

        // Merge the flattened data with the existing.
        return zipAll(columnarTable).map((row) => {
            const newRow = { ...previousData[0] };
            row.forEach((value, columnI) => {
                newRow[this.parameterFlattener.flattened[columnI].finalColumnName] = value;
            });

            return newRow;
        });
    }
}
