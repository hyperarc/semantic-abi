import {SubsequentStep} from "semanticabi/transform/steps/SubsequentStep";
import {Step} from "semanticabi/transform/steps/Step";
import {AbiSchema} from "semanticabi/transform/steps/AbiSchema";
import {ParameterFlattener} from "semanticabi/transform/steps/ParameterFlattener";
import {EthBlock} from "semanticabi/metadata/EthBlock";
import {EthTransaction} from "semanticabi/metadata/EthTransaction";
import {TransformItem} from "semanticabi/transform/steps/TransformItem";
import {JsonObject} from "common/CommonTypes";

/**
 * Adds all included parameters from the abi item to the schema and results.
 */
export class FlattenStep extends SubsequentStep {

    public readonly schema: AbiSchema;
    private readonly parameterFlattener: ParameterFlattener;

    constructor(previousStep: Step) {
        super(previousStep);

        this.parameterFlattener = new ParameterFlattener(this.previousStep.abiItem);
        this.schema = this.previousStep.schema.withColumns(this.parameterFlattener.datasetColumns);
    }

    protected innerTransformItem(
        block: EthBlock,
        transaction: EthTransaction,
        item: TransformItem,
        previousData: JsonObject[]
    ): JsonObject[] {
        return previousData.map(row => {
            this.parameterFlattener.flattened.forEach(p => {
                row[p.finalColumnName] = p.flattenedValue(item.decodedResult);
            });

            return row;
        });
    }

}