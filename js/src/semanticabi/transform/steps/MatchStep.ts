import {SubsequentStep} from "semanticabi/transform/steps/SubsequentStep";
import {Step} from "semanticabi/transform/steps/Step";
import {Match} from "semanticabi/abi/item/semantic/Match";
import {AbiSchema} from "semanticabi/transform/steps/AbiSchema";
import { JsonObject } from "common/CommonTypes";
import {MatchCardinality} from "semanticabi/abi/item/semantic/MatchCardinality";
import {SemanticAbiExecutionError} from "semanticabi/abi/item/semantic/SemanticAbiExecutionError";
import {DatasetColumn} from "semanticabi/transform/column/DatasetColumn";
import { Optional } from "common/Optional";
import {EthBlock} from "semanticabi/metadata/EthBlock";
import {EthTransaction} from "semanticabi/metadata/EthTransaction";
import {TransformItem} from "semanticabi/transform/steps/TransformItem";
import {SemanticAbi} from "semanticabi/abi/SemanticAbi";
import {SemanticAbiItem} from "semanticabi/abi/item/semantic/SemanticAbiItem";
import { MatchType } from "semanticabi/abi/item/semantic/MatchType";
import {InitStep} from "semanticabi/transform/steps/InitStep";
import {FlattenStep} from "semanticabi/transform/steps/FlattenStep";
import {TokenTransferStep} from "semanticabi/transform/steps/TokenTransferStep";

/**
 * Step that "joins" the current item with other items based on the match predicates.
 */
export class MatchStep extends SubsequentStep {

    private readonly _matchesAndSteps: [Match, Step][];
    public readonly schema: AbiSchema;

    constructor(previousStep: Step, matchesAndSteps: [Match, Step][]) {
        super(previousStep);

        this._matchesAndSteps = matchesAndSteps;
        this.schema = MatchStep.buildSchema(previousStep.schema, matchesAndSteps);
    }

    get shouldTransform(): boolean {
        return this.abiItem.properties.matches !== null;
    }

    protected innerTransformItem(
        block: EthBlock,
        transaction: EthTransaction,
        item: TransformItem,
        previousData: JsonObject[]
    ): JsonObject[] {
        // Iteratively reduce the previous data for every specified match, adding more columns and sometimes more rows
        // for cases of MANY matches.
        return this._matchesAndSteps.reduce((currentData, [match, step]) => {
            // Sanity check that we aren't getting into combinatorics.
            if (match.cardinality === MatchCardinality.MANY && currentData.length > 1) {
                throw new SemanticAbiExecutionError('Only a single row of data can be matched with a "many" match.');
            }

            // Get the decoded data for the items to match against.
            const transformedMatchRows: JsonObject[] = step.transform(block, transaction);
            // Apply the match for each current row of data.
            return currentData.flatMap(row => {
                // Figure out the actual matched rows.
                const matchedRows = transformedMatchRows.filter(
                    r => match.predicates.every(p => p.matches(row, r))
                );

                return MatchStep.mergeMatches(row, matchedRows, match, step);
            });
        }, previousData);
    }

    private static buildSchema(previousSchema: AbiSchema, matchesAndSteps: [Match, Step][]): AbiSchema {
        let newSchema = previousSchema;
        for (const [match, step] of matchesAndSteps) {
            match.validateSchemas(newSchema, step.schema);
            newSchema = newSchema.mergeSchema(step.schema, match.makePrefixedColumnName.bind(match));
        }
        return newSchema;
    }

    /**
     * Merge a given row with matched rows.
     */
    private static mergeMatches(
        row: JsonObject,
        matchedRows: JsonObject[],
        itemMatch: Match,
        step: Step
    ): JsonObject[] {
        // make sure the cardinality of the matches are correct, if so we can process the matches generically
        itemMatch.cardinality.assertMatched(matchedRows, itemMatch);

        const mergedRows: JsonObject[] = [];
        if (matchedRows.length === 0) {
            // no match, populate with nulls
            mergedRows.push(MatchStep.appendMatchedData(row, Optional.none(), step.schema.columns, itemMatch));
        } else {
            // create a row per match
            matchedRows.forEach(matchedRow =>
                mergedRows.push(MatchStep.appendMatchedData(
                    row, Optional.of(matchedRow), step.schema.columns, itemMatch
                ))
            );
        }

        return mergedRows;
    }

    private static appendMatchedData(
        row: JsonObject,
        // support optional matches which will populate matched keys with nulls
        matchedRow: Optional<JsonObject>,
        matchedColumns: DatasetColumn[],
        itemMatch: Match
    ): JsonObject {
        const mergedRow = { ...row };
        matchedColumns.forEach(c =>
            mergedRow[itemMatch.makePrefixedColumnName(c.name)] = matchedRow.map(r => r[c.name]).nullable
        );

        return mergedRow;
    }

}

/**
 * A precomputed collection of steps for use in a MatchStep so that if there are multiple matches against the same item,
 * we only generate the step for that item once. Each matched item simply just flattens the parameters and does not
 * include any transform error to avoid appending additional transform error columns.
 */
export class AbiMatchSteps {

    private constructor(
        private readonly eventMatchStepsBySignature: Map<string, Step>,
        private readonly functionMatchStepsBySignature: Map<string, Step>
    ) { }

    public stepsForMatch(matches: Match[]): [Match, Step][] {
        return matches.map(match => {
            // figure out the step for the given match
            const getStep = (): Step => {
                switch (match.type) {
                    case MatchType.EVENT:
                        return this.eventMatchStepsBySignature.get(match.signature.get());
                    case MatchType.FUNCTION:
                        return this.functionMatchStepsBySignature.get(match.signature.get());
                    case MatchType.TRANSFER:
                        return new TokenTransferStep();
                }
            };

            return [match, getStep()];
        });
    }

    public static fromAbi(abi: SemanticAbi, primaryItems: SemanticAbiItem[]): AbiMatchSteps {
        const eventMatchStepsBySignature: Map<string, Step> = new Map();
        const functionMatchStepsBySignature: Map<string, Step> = new Map();

        primaryItems
            // Flatten all matches so we can process them in a single pass.
            .flatMap(item =>
                item.properties.matches.map(
                    // Skip matches without signatures since they are for Transfers and don't need to go into the event
                    // or function lookups.
                    m => m.matches.filter(m => m.signature.isPresent)
                ).array.flat()
            )
            .forEach(match => {
                // For each unique match signature, create a step for it.
                const signature = match.signature.get();
                if (match.type === MatchType.EVENT && !eventMatchStepsBySignature.has(signature)) {
                    eventMatchStepsBySignature.set(
                        signature,
                        new FlattenStep(new InitStep(abi, abi.eventBySignature(signature).get()))
                    );
                } else if (match.type === MatchType.FUNCTION && !eventMatchStepsBySignature.has(signature)) {
                    functionMatchStepsBySignature.set(
                        signature,
                        new FlattenStep(new InitStep(abi, abi.functionBySignature(signature).get()))
                    );
                }
            });

        return new AbiMatchSteps(eventMatchStepsBySignature, functionMatchStepsBySignature);
    }

}
