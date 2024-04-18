import {SubsequentStep} from "semanticabi/transform/steps/SubsequentStep";
import {Step} from "semanticabi/transform/steps/Step";
import {AbiSchema} from "semanticabi/transform/steps/AbiSchema";
import {EthBlock} from "semanticabi/metadata/EthBlock";
import {EthTransaction} from "semanticabi/metadata/EthTransaction";
import {TransformItem} from "semanticabi/transform/steps/TransformItem";
import {JsonObject} from "common/CommonTypes";

/**
 * Special step that adds a column to the schema for holding errors that occurred during the transform. This doesn't
 * actually add the error to the data, but only informs the final transform process that it should include any errors
 * in the data.
 */
export class TransformErrorStep extends SubsequentStep {

    public readonly schema: AbiSchema;

    constructor(previousStep: Step) {
        super(previousStep);

        this.schema = this.previousStep.schema.withColumns([Step.TRANSFORM_ERROR_COLUMN]);
    }

    protected innerTransformItem(
        block: EthBlock,
        transaction: EthTransaction,
        item: TransformItem,
        previousData: JsonObject[]
    ): JsonObject[] {
        return previousData;
    }

}