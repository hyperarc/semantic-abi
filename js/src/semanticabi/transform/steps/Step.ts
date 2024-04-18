import {SemanticAbi} from "semanticabi/abi/SemanticAbi";
import {AbiSchema} from "semanticabi/transform/steps/AbiSchema";
import {SemanticAbiItem} from "semanticabi/abi/item/semantic/SemanticAbiItem";
import {EthTransaction} from "semanticabi/metadata/EthTransaction";
import {TransformItem} from "semanticabi/transform/steps/TransformItem";
import {EthBlock} from "semanticabi/metadata/EthBlock";
import {JsonObject} from "common/CommonTypes";
import {DataType} from "semanticabi/transform/column/DataType";


/**
 * Represents a step in the transaction transformation process. Each step takes the output of the previous step and
 * applies the next set of transformations.
 */
export abstract class Step {

    static readonly TRANSFORM_ERROR_COLUMN = DataType.STRING.column('transform_error');

    abstract get schema(): AbiSchema;

    abstract get abi(): SemanticAbi;

    abstract get abiItem(): SemanticAbiItem;

    abstract get shouldTransform(): boolean;

    abstract innerTransform(block: EthBlock, transaction: EthTransaction): [TransformItem, JsonObject[]][];

    /**
     * Returns the transformed block and transaction data as a list of results.
     */
    transform(block: EthBlock, transaction: EthTransaction): JsonObject[] {
        const results: JsonObject[] = [];
        const schema = this.schema;

        for (const [item, transformedRows] of this.innerTransform(block, transaction)) {
            for (const transformedRow of transformedRows) {
                const finalRow = schema.columns.reduce<JsonObject>((row, column) => {
                    try {
                        row[column.name] = (column.name === Step.TRANSFORM_ERROR_COLUMN.name) ?
                            item.transformError.nullable :
                            column.transform(transformedRow);
                    } catch (e) {
                        item.addTransformError(e.toString());
                    }
                    return row;
                }, {});
                results.push(finalRow);
            }
        }

        return results;
    }

}