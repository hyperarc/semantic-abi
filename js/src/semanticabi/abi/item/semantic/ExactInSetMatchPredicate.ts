import {JsonObject} from "common/CommonTypes";
import { Optional } from "common/Optional";
import {MatchPredicate} from "semanticabi/abi/item/semantic/MatchPredicate";
import {SemanticAbiValidationError} from "semanticabi/abi/item/semantic/SemanticAbiValidateable";

export type ExactInSetMatchJson = {
    source: string,
    matched: string[]
}

/**
 * Match predicate for a source column to a set of columns to match against to see if the value in the source exists in
 * any column of the to be matched set.
 */
export class ExactInSetMatchPredicate implements MatchPredicate {

    public readonly sourceColumnNames: Set<string>;
    public readonly matchedColumnNames: Set<string>;

    constructor(
        private readonly source: string,
        matched: string[],
    ) {
        this.sourceColumnNames = new Set([this.source]);
        this.matchedColumnNames = new Set(matched);
    }

    matches(sourceRow: JsonObject, matchedRow: JsonObject): boolean {
        return Array.from(this.matchedColumnNames)
            .some(matched => sourceRow[this.source] === matchedRow[matched]);
    }

    validate(): Optional<SemanticAbiValidationError> {
        return Optional.none();
    }

    static fromJSON(json: ExactInSetMatchJson): ExactInSetMatchPredicate {
        return new ExactInSetMatchPredicate(json.source, json.matched);
    }

}
