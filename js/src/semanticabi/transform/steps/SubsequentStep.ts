import {SemanticAbi} from "semanticabi/abi/SemanticAbi";
import {SemanticAbiItem} from "semanticabi/abi/item/semantic/SemanticAbiItem";
import {EthTransaction} from "semanticabi/metadata/EthTransaction";
import {TransformItem} from "semanticabi/transform/steps/TransformItem";
import {EthBlock} from "semanticabi/metadata/EthBlock";
import {JsonObject} from "common/CommonTypes";
import {Step} from "semanticabi/transform/steps/Step";

/**
 * Steps that have a prior step.
 */
export abstract class SubsequentStep extends Step {

    constructor(
        protected readonly previousStep: Step
    ) {
        super();
    }

    /**
     * Apply a transform to an individual event or function, given any previous data that has already been transformed.
     * The vast majority of steps should only need to implement this method, and use the default implementation of
     * inner_transform.
     */
    protected abstract innerTransformItem(
        block: EthBlock,
        transaction: EthTransaction,
        item: TransformItem,
        previousData: JsonObject[]
    ): JsonObject[];

    get abi(): SemanticAbi {
        return this.previousStep.abi;
    }

    get abiItem(): SemanticAbiItem {
        return this.previousStep.abiItem;
    }

    get shouldTransform(): boolean {
        return true;
    }

    /**
     * Returns a list of tuples of the current event or function being processed and the results for that item.
     */
    innerTransform(block: EthBlock, transaction: EthTransaction): [TransformItem, JsonObject[]][] {
        const previousResults = this.previousStep.innerTransform(block, transaction);

        if (!this.shouldTransform) {
            return previousResults;
        }

        const results: Array<[TransformItem, Array<Record<string, any>>]> = [];
        for (const [resultItem, previousData] of previousResults) {
            try {
                if (resultItem.hasTransformError) {
                    results.push([resultItem, previousData]);
                } else {
                    const transformedRows = this.innerTransformItem(block, transaction, resultItem, previousData);
                    results.push([resultItem, transformedRows]);
                }
            } catch (e) {
                resultItem.addTransformError(e.toString());
                results.push([resultItem, previousData]);
                // Log error if necessary, adapting to your logging framework
            }
        }

        return results;
    }

}