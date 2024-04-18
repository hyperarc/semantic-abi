import {SemanticAbiValidationError} from "semanticabi/abi/item/semantic/SemanticAbiValidateable";
import {Optional} from "common/Optional";
import {Match, MatchJson} from "semanticabi/abi/item/semantic/Match";
import {MatchCardinality} from "semanticabi/abi/item/semantic/MatchCardinality";
import {SemanticItemTransform} from "semanticabi/abi/item/semantic/SemanticItemTransform";
import {SemanticParameters} from "semanticabi/abi/item/semantic/SemanticParameters";
import {AbiItem} from "semanticabi/abi/item/AbiItem";
import {TupleParameter} from "semanticabi/abi/item/Parameter";

export class Matches implements SemanticItemTransform {

    constructor(
        public readonly matches: Match[]
    ) { }

    static fromJSON(json: MatchJson[]): Matches {
        return new Matches(json.map(matchJson => Match.fromJSON(matchJson)));
    }

    validate(item: AbiItem, inputAndOutputs: SemanticParameters[]): Optional<SemanticAbiValidationError> {
        let hasManyAssert = false;
        const prefixesBySignature: Map<string, Set<string>> = new Map();

        for (const match of this.matches) {
            if (match.signature.map(s => s === item.signature).bool) {
                return SemanticAbiValidationError.some(`Cannot match item signature "${item.signature}" with itself.`);
            }

            // make sure match prefix is not the same as a tuple parameter incase it gets exploded
            const prefixValidation = inputAndOutputs.reduce(
                (result, parameters) => result.orElse(
                    () => parameters.get(match.prefix)
                        .filter(p => p.parameter instanceof TupleParameter)
                        .map(() => new SemanticAbiValidationError(`Prefix "${match.prefix}" cannot be the name of a tuple parameter.`))
                ),
                Optional.none<SemanticAbiValidationError>()
            );
            if (prefixValidation.isPresent) {
                return prefixValidation;
            }

            if (match.cardinality === MatchCardinality.MANY) {
                if (hasManyAssert) {
                    return SemanticAbiValidationError.some('Cannot have multiple matches that assert "many".');
                }
                hasManyAssert = true;
            }

            // see if there are any duplicate signatures for the same prefix
            const duplicateSignatures: Optional<boolean> = match.signature.flatMap(signature => {
                if (!prefixesBySignature.has(signature)) {
                    prefixesBySignature.set(signature, new Set<string>());
                }

                if (prefixesBySignature.get(signature).has(match.prefix)) {
                    return Optional.some(true);
                }

                prefixesBySignature.get(signature).add(match.prefix);
                return Optional.none();
            });

            if (duplicateSignatures.bool) {
                return SemanticAbiValidationError.some(`Cannot have multiple matches of the same signature '${match.signature}' with the same prefix '${match.prefix}'`);
            }
        }

        return SemanticAbiValidationError.first(this.matches);
    }

}