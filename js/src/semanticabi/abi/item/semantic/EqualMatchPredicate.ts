import {JsonObject} from "common/CommonTypes";
import {MatchPredicate} from "semanticabi/abi/item/semantic/MatchPredicate";
import {Optional} from "common/Optional";
import {SemanticAbiValidationError} from "semanticabi/abi/item/semantic/SemanticAbiValidateable";

export type EqualMatchJson = {
    source: string,
    matched: string
}

/**
 * Match predicate on exact equality of two values.
 */
export class EqualMatchPredicate implements MatchPredicate {

    public readonly sourceColumnNames: Set<string>;
    public readonly matchedColumnNames: Set<string>;

    constructor(
        private readonly source: string,
        private readonly matched: string
    ) {
        this.sourceColumnNames = new Set([this.source]);
        this.matchedColumnNames = new Set([this.matched]);
    }

    matches(sourceRow: JsonObject, matchedRow: JsonObject): boolean {
        return sourceRow[this.source] === matchedRow[this.matched];
    }

    validate(): Optional<SemanticAbiValidationError> {
        return Optional.none();
    }

    static fromJSON(json: EqualMatchJson): EqualMatchPredicate {
        return new EqualMatchPredicate(json.source, json.matched);
    }

}
