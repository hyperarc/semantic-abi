import {Enum} from "common/Enum";
import {JsonObject} from "common/CommonTypes";
import {Match} from "semanticabi/abi/item/semantic/Match";
import {SemanticAbiExecutionError} from "semanticabi/abi/item/semantic/SemanticAbiExecutionError";

export class MatchCardinality extends Enum {

    // exactly 1 match
    static readonly ONLY_ONE = new this(
        'onlyOne',
        (matchedRows: JsonObject[]): boolean => matchedRows.length === 1
    );
    // one or more matches
    static readonly MANY = new this(
        'many',
        (matchedRows: JsonObject[]): boolean => matchedRows.length > 0
    );
    // 0 or 1 match
    static readonly OPTIONAL_ONE = new this(
        'optionalOne',
        (matchedRows: JsonObject[]): boolean => matchedRows.length <= 1
    );

    constructor(
        name: string,
        // return false if the matched rows are of the wrong cardinality
        private readonly assert: (matchedRows: JsonObject[]) => boolean
    ) {
        super(name);
    }

    assertMatched(matchedRows: any[], match: Match) {
        if (!this.assert(matchedRows)) {
            let errorMessage = `Matched cardinality of '${matchedRows.length}' does not match expected cardinality for '${this.name}'`;
            match.signature.forEach(s => errorMessage += ` with signature '${s}'`);
            throw new SemanticAbiExecutionError(errorMessage + '.');
        }
    }

}
MatchCardinality.finalize();
