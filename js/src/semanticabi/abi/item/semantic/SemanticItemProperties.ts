import {Optional} from "common/Optional";
import {Explode, ExplodeJson} from "semanticabi/abi/item/semantic/Explode";
import {ExpressionJson, Expressions} from "semanticabi/abi/item/semantic/Expressions";
import {Matches} from "semanticabi/abi/item/semantic/Matches";
import {MatchJson} from "semanticabi/abi/item/semantic/Match";
import {
    SemanticAbiValidateable,
    SemanticAbiValidationError
} from "semanticabi/abi/item/semantic/SemanticAbiValidateable";
import {MatchCardinality} from "semanticabi/abi/item/semantic/MatchCardinality";


export class SemanticItemProperties implements SemanticAbiValidateable {

    constructor(
        public readonly isPrimary: boolean,
        public readonly explode: Optional<Explode>,
        public readonly matches: Optional<Matches>,
        public readonly expressions: Optional<Expressions>
    ) { }

    validate(): Optional<SemanticAbiValidationError> {
        if (
            !this.isPrimary
            && Optional.any([this.explode, this.matches, this.expressions]).isPresent
        ) {
            return SemanticAbiValidationError.some('Non-primary ABI item may not have "explode", "matches", or "expressions".');
        }

        return this.explode
            .flatMap(() => this.matches)
            .flatMap<SemanticAbiValidationError>(matches => {
                // check cardinality
                for (const match of matches.matches) {
                    if (match.cardinality === MatchCardinality.MANY) {
                        return SemanticAbiValidationError.some('Cannot have a match that asserts "many" and an explode on the same item.');
                    }
                }

                return Optional.none();
            });
    }

    static fromJSON(json: SemanticAbiItemPropertiesJson): SemanticItemProperties {
        return new SemanticItemProperties(
            json['@isPrimary'],
            Optional.of(json['@explode']).map(Explode.fromJSON),
            Optional.of(json['@matches']).map(Matches.fromJSON),
            // TODO ZZ implement expressions
            Optional.none()
        );
    }

}

export type SemanticAbiItemPropertiesJson = {

    '@isPrimary'?: boolean,
    '@explode'?: ExplodeJson,
    '@matches'?: MatchJson[],
    '@expressions'?: ExpressionJson[]

}
