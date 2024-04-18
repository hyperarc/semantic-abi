import {SemanticParameter, SemanticParameters} from "semanticabi/abi/item/semantic/SemanticParameters";
import {SemanticItemTransform} from "semanticabi/abi/item/semantic/SemanticItemTransform";
import {SemanticAbiValidationError} from "semanticabi/abi/item/semantic/SemanticAbiValidateable";
import {Left, Right} from "common/Either";
import {Optional} from "common/Optional";
import {AbiItem} from "semanticabi/abi/item/AbiItem";

export type ExplodeJson = {
    paths: string[]
}

/**
 * Explode the parameters into their parts.
 */
export class Explode implements SemanticItemTransform {

    public readonly pathParts: Map<string, string[]>;

    constructor(
        public readonly paths: string[]
    ) {
        this.pathParts = new Map(paths.map(path => [path, path.split('.')] as [string, string[]]));
    }

    validate(item: AbiItem, inputAndOutputs: SemanticParameters[]): Optional<SemanticAbiValidationError> {
        for (const [path, pathParts] of this.pathParts) {
            const pathValidation = inputAndOutputs.find(parameters => parameters.has(pathParts[0]))
                .getAt(pathParts)
                // a couple more checks on the resolved parameter
                .flatMap<SemanticParameter>(parameter => {
                    if (parameter.exclude) {
                        return new Left(new SemanticAbiValidationError(`Explode path '${path}' cannot reference an excluded parameter.`));
                    }
                    if (!parameter.parameter.isArray || parameter.parameter.isArrayOfArrays) {
                        return new Left(new SemanticAbiValidationError(`Explode path '${path}' is not a one dimensional array that can be exploded.`));
                    }

                    return new Right(parameter);
                })
                // swap to return right as the optional error
                .swap()
                .optional();

            if (pathValidation.isPresent) {
                return pathValidation;
            }
        }

        return Optional.none();
    }

    static fromJSON(json: ExplodeJson): Explode {
        return new Explode(json['paths']);
    }

}