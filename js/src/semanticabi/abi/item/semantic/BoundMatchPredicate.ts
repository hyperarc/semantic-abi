import {JsonObject} from "common/CommonTypes";
import { Optional } from "common/Optional";
import {MatchPredicate} from "semanticabi/abi/item/semantic/MatchPredicate";
import {SemanticAbiValidationError} from "semanticabi/abi/item/semantic/SemanticAbiValidateable";

export type BoundMatchJson = {
    source: string,
    matched: string,
    lower: number,
    upper: number
}

/**
 * Match predicate on numeric values comparing the "matched" with the source value given an upper and lower bound
 * expressed as a percentage of the source value.
 */
export class BoundMatchPredicate implements MatchPredicate {

    public readonly sourceColumnNames: Set<string>;
    public readonly matchedColumnNames: Set<string>;

    constructor(
        private readonly source: string,
        private readonly matched: string,
        // The lower and upper bounds expressed as percentages of the source value, 1 being 100% of the source value.
        public readonly lower: number,
        public readonly upper: number
    ) {
        this.sourceColumnNames = new Set([this.source]);
        this.matchedColumnNames = new Set([this.matched]);
    }

    matches(sourceRow: JsonObject, matchedRow: JsonObject): boolean {
        const value = sourceRow[this.source];
        const matchedValue = matchedRow[this.matched];

        if (this.lower !== null && matchedValue < this.lower * value) {
            return false;
        }
        if (this.upper !== null && matchedValue > this.upper * value) {
            return false;
        }

        return true;
    }

    validate(): Optional<SemanticAbiValidationError> {
        if (this.lower == null && this.upper == null) {
            return SemanticAbiValidationError.some('Bound match must specify at least one of "lower" or "upper".');
        }

        if (this.lower != null && this.upper != null && this.lower > this.upper) {
            return SemanticAbiValidationError.some('Bound match "lower" must be less than "upper".');
        }

        return Optional.none();
    }

    static fromJSON(json: BoundMatchJson): BoundMatchPredicate {
        return new BoundMatchPredicate(json.source, json.matched, json.lower, json.upper);
    }

}
