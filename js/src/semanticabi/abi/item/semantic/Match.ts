import {JsonObject} from "common/CommonTypes";
import {MatchType} from "semanticabi/abi/item/semantic/MatchType";
import {MatchCardinality} from "semanticabi/abi/item/semantic/MatchCardinality";
import {EqualMatchJson, EqualMatchPredicate} from "semanticabi/abi/item/semantic/EqualMatchPredicate";
import {MatchPredicate} from "semanticabi/abi/item/semantic/MatchPredicate";
import {BoundMatchJson, BoundMatchPredicate} from "semanticabi/abi/item/semantic/BoundMatchPredicate";
import {ExactInSetMatchJson, ExactInSetMatchPredicate} from "semanticabi/abi/item/semantic/ExactInSetMatchPredicate";
import {Optional} from "common/Optional";
import {
    SemanticAbiValidateable,
    SemanticAbiValidationError
} from "semanticabi/abi/item/semantic/SemanticAbiValidateable";
import {SemanticAbiParseError} from "semanticabi/abi/item/semantic/SemanticAbiParseError";
import {AbiSchema} from "semanticabi/transform/steps/AbiSchema";
import {SemanticAbiExecutionError} from "semanticabi/abi/item/semantic/SemanticAbiExecutionError";

export type MatchJson = {
    type: string;
    assert: string;
    signature?: string;
    prefix: string;
    predicates: JsonObject[];
};

/**
 * Match criteria for a row.
 */
export class Match implements SemanticAbiValidateable {

    constructor(
        // Type of data to match for.
        public readonly type: MatchType,
        // Signature hash of the log or function data we're matching, none for transfers.
        public readonly signature: Optional<string>,
        // Prefix used for matched columns.
        public readonly prefix: string,
        // Cardinality assertions for matches.
        public readonly cardinality: MatchCardinality,
        // Predicates to do the actual matching.
        public readonly predicates: MatchPredicate[]
    ) { }

    /**
     * Validate the match definition.
     */
    validate(): Optional<SemanticAbiValidationError> {
        if (this.signature.isNone && this.type !== MatchType.TRANSFER) {
            return SemanticAbiValidationError.some('Match must specify "signature" unless it is a "transfer" match.');
        }

        return SemanticAbiValidationError.first(this.predicates);
    }

    /**
     * Validate the match given source and matched schemas.
     */
    validateSchemas(sourceSchema: AbiSchema, matchedSchema: AbiSchema) {
        for (const predicate of this.predicates) {
            for (const sourceColumnName of predicate.sourceColumnNames) {
                if (!sourceSchema.hasColumn(sourceColumnName)) {
                    throw new SemanticAbiExecutionError(`Unknown source column referenced in match predicate of prefix '${this.prefix}': ${sourceColumnName}.`);
                }
            }

            for (const matchedColumnName of predicate.matchedColumnNames) {
                if (!matchedSchema.hasColumn(matchedColumnName)) {
                    throw new SemanticAbiExecutionError(`Unknown matched column referenced in match predicate of prefix '${this.prefix}': ${matchedColumnName}.`);
                }
            }
        }
    }

    makePrefixedColumnName(name: string): string {
        return `${this.prefix}_${name}`;
    }

    static fromJSON(json: MatchJson): Match {
        return new Match(
            MatchType.get(json.type),
            Optional.of(json.signature),
            json.prefix,
            MatchCardinality.get(json.assert),
            json.predicates.map(predicate => Match.fromPredicateJson(predicate))
        );
    }

    static fromPredicateJson(json: JsonObject): MatchPredicate {
        switch (json.type) {
            case 'equal':
                return EqualMatchPredicate.fromJSON(json as EqualMatchJson);
            case 'bound':
                return BoundMatchPredicate.fromJSON(json as BoundMatchJson);
            case 'in':
                return ExactInSetMatchPredicate.fromJSON(json as ExactInSetMatchJson);
            default:
                throw new SemanticAbiParseError(`Unknown predicate type: ${json.type}.`);
        }
    }

}