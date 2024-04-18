import {JsonObject} from "common/CommonTypes";
import {SemanticAbiValidateable} from "semanticabi/abi/item/semantic/SemanticAbiValidateable";

export interface MatchPredicate extends SemanticAbiValidateable {

    /**
     * Returns true if the sourceRow matches the target matchedRow.
     */
    matches(sourceRow: JsonObject, matchedRow: JsonObject): boolean;

    /**
     * Return the set of column names that we're using to match.
     */
    get sourceColumnNames(): Set<string>;

    /**
     * Return the set of column names that we're matching to in the target.
     */
    get matchedColumnNames(): Set<string>;

}
