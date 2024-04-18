import {SemanticAbi, SemanticAbiJson} from "semanticabi/abi/SemanticAbi";
import {Step} from "semanticabi/transform/steps/Step";
import {AbiSchema} from "semanticabi/transform/steps/AbiSchema";
import {SemanticAbiItem} from "semanticabi/abi/item/semantic/SemanticAbiItem";
import {AbiMatchSteps, MatchStep} from "semanticabi/transform/steps/MatchStep";
import {InitStep} from "semanticabi/transform/steps/InitStep";
import {DefaultColumnsStep} from "semanticabi/transform/steps/DefaultColumnsStep";
import {FlattenStep} from "semanticabi/transform/steps/FlattenStep";
import {ExplodeStep} from "semanticabi/transform/steps/ExplodeStep";
import {ExplodeIndexStep} from "semanticabi/transform/steps/ExplodeIndexStep";
import {TransformErrorStep} from "semanticabi/transform/steps/TransformErrorStep";
import {EvmChain} from "semanticabi/metadata/EvmChain";
import {EthBlock} from "semanticabi/metadata/EthBlock";
import {DataType} from "semanticabi/transform/column/DataType";
import {JsonObject} from "common/CommonTypes";

/**
 * Given a Semantic ABI definition, this will build the necessary transformation pipeline to transform a block with
 * transactions that contains a log or trace that is marked as a primary item in the ABI, and then transform those
 * transactions.
 */
export class SemanticTransformer {

    private readonly abi: SemanticAbi;
    private readonly pipelineByTopic: Map<string, Step>;
    public readonly schema: AbiSchema;

    /**
     * Constructs a SemanticTransformer given a JSON representation of a Semantic ABI. Throws an InvalidAbiException
     * if there are any problems with the ABI that would prevent it from being able to construct a valid schema.
     */
    constructor(abiJson: SemanticAbiJson) {
        this.abi = new SemanticAbi(abiJson);

        const primaryItems: SemanticAbiItem[] = [...this.abi.events.values(), ...this.abi.functions.values()]
            .filter(item => item.properties.isPrimary);

        this.pipelineByTopic = new Map(
            primaryItems.map((item) => [
                item.rawItem.hash,
                SemanticTransformer.buildPipeline(this.abi, item, AbiMatchSteps.fromAbi(this.abi, primaryItems)),
            ])
        );

        // merge all the schemas together
        this.schema = Array.from(this.pipelineByTopic.values())
            .map((step) => step.schema)
            .reduce((prevSchema, nextSchema) => prevSchema.mergeSchema(nextSchema, (n) => n, true));
    }

    /**
     * Given a block, goes through each transaction, finding any that have logs or traces that match any of the
     * primary item topics, and transforms those primary items into rows.
     */
    transform(block: EthBlock): JsonObject[] {
        if (!this.isValidForChain(block.chain)) {
            return [];
        }

        return block.transactions
            .flatMap((transaction) =>
                Array.from(this.pipelineByTopic.entries())
                    // figure out which pipelines are applicable
                    .filter(([topic, _]) => transaction.logsByTopic.has(topic) || transaction.tracesByTopic.has(topic))
                    // apply the pipeline to the transaction and flatten out the results into a single table
                    .flatMap(([_, step]) => step.transform(block, transaction))
            )
            .map((row) => {
                // Pad out any missing columns with null so we have consistent schema.
                this.schema.columns
                    .filter((column) => !(column.name in row))
                    .forEach((column) => row[column.name] = null);
                return row;
            });
    }

    /**
     * Does this ABI apply to the given chain?
     */
    isValidForChain(chain: EvmChain): boolean {
        return this.abi.chains.has(chain);
    }

    /**
     * Returns the metadata for the columns.
     */
    get metadata(): [string, DataType][] {
        return this.schema.columns.map((c) => [c.name, c.dataType]);
    }

    /**
     * Construct the set of steps for transforming a primary abi item.
     */
    private static buildPipeline(abi: SemanticAbi, item: SemanticAbiItem, matchSteps: AbiMatchSteps): Step {
        let step: Step = new InitStep(abi, item);
        step = new DefaultColumnsStep(step);
        step = new FlattenStep(step);
        step = new ExplodeStep(step);
        step = new MatchStep(
            step,
            item.properties.matches.map(matches => matchSteps.stepsForMatch(matches.matches)).getOr([])
        );
        step = new ExplodeIndexStep(step);
        step = new TransformErrorStep(step);
        return step;
    }


}