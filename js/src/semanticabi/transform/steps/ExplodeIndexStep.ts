import {SubsequentStep} from "semanticabi/transform/steps/SubsequentStep";
import {Step} from "semanticabi/transform/steps/Step";
import {AbiSchema} from "semanticabi/transform/steps/AbiSchema";
import {DataType} from "semanticabi/transform/column/DataType";
import {EthBlock} from "semanticabi/metadata/EthBlock";
import {EthTransaction} from "semanticabi/metadata/EthTransaction";
import {TransformItem} from "semanticabi/transform/steps/TransformItem";
import {JsonObject} from "common/CommonTypes";

const EXPLODE_INDEX_COLUMN = DataType.NUMBER.column('explodeIndex');

/**
 * After the Explode and Match steps, adds a unique index for each row of exploded or "many" matched data.
 */
export class ExplodeIndexStep extends SubsequentStep {

    public readonly schema: AbiSchema;

    constructor(previousStep: Step) {
        super(previousStep);

        this.schema = this.previousStep.schema.withColumns([EXPLODE_INDEX_COLUMN]);
    }

    protected innerTransformItem(
        block: EthBlock,
        transaction: EthTransaction,
        item: TransformItem,
        previousData: JsonObject[]
    ): JsonObject[] {
        return previousData.map((row, i) => {
            row[EXPLODE_INDEX_COLUMN.name] = i;
            return row;
        });
    }

}