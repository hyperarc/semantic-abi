import {Optional} from "common/Optional";

/**
 * Parts of the semantic ABI that can be validated.
 *
 * @author zuyezheng
 */
export interface SemanticAbiValidateable {

    validate(): Optional<SemanticAbiValidationError>;

}

/**
 * Error validating something about the ABI.
 */
export class SemanticAbiValidationError {

    constructor(
        public readonly message: string
    ) { }

    static some(message: string): Optional<SemanticAbiValidationError> {
        return Optional.some(new SemanticAbiValidationError(message));
    }

    /**
     * Return the first validation error or none.
     */
    static first(validateables: SemanticAbiValidateable[]): Optional<SemanticAbiValidationError> {
        return validateables.reduce(
            // keep validating until we reach the end or we've found the first validation error
            (acc, validateable) => acc.orElse(() => validateable.validate())
        , Optional.none<SemanticAbiValidationError>());
    }

}