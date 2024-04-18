import {Parameter, TupleParameter} from "semanticabi/abi/item/Parameter";
import {Optional} from "common/Optional";
import {InvalidAbiError} from "semanticabi/abi/InvalidAbiError";
import {
    ParameterTransformJson,
    SemanticParameterTransform
} from "semanticabi/abi/item/semantic/SemanticParameterTransform";
import {SemanticAbiValidationError} from "semanticabi/abi/item/semantic/SemanticAbiValidateable";
import {ParameterJson} from "semanticabi/abi/item/Parameters";
import {Either, Left} from "common/Either";

/**
 * Extends Parameters with semantics.
 */
export class SemanticParameters {

    public readonly parameters: Map<string, SemanticParameter>;

    constructor(parameters: SemanticParameter[]) {
        this.parameters = new Map(parameters.map(p => [p.name, p]));
    }

    /**
     * Return the parameter at the given path or error if invalid.
     */
    getAt(pathParts: string[]): Either<SemanticAbiValidationError, SemanticParameter> {
        return Optional.of(this.parameters.get(pathParts[0]))
            // recursively traverse the rest of the path
            .flatMap(p => p.getAt(pathParts.slice(1)))
            // missing parameter
            .getOr(new Left(new SemanticAbiValidationError(`Parameter not found at "${pathParts.join('.')}".`)));
    }

    has(name: string): boolean {
        return this.parameters.has(name);
    }

    get(name: string): Optional<SemanticParameter> {
        return Optional.of(this.parameters.get(name));
    }

    static fromParameters(parameters: Parameter[], parametersJson: SemanticParameterJson[]): SemanticParameters {
        const parameterNames = new Set<string>();
        for (const parameter of parameters) {
            if (parameterNames.has(parameter.name)) {
                throw new InvalidAbiError(`Parameter '${parameter.name}' is duplicated.`);
            }
            parameterNames.add(parameter.name);
        }

        const parametersByNameJson = new Map<string, SemanticParameterJson>(parametersJson.map(p => [p['name'], p]));
        return new SemanticParameters(
            parameters.map(p => SemanticParameter.fromJSON(p, parametersByNameJson.get(p.name)))
        );
    }

}

export interface SemanticParameterJson extends ParameterJson {
    '@transform'?: ParameterTransformJson;
    '@exclude'?: boolean;

    // override components with additional semantic properties
    'components'?: SemanticParameterJson[];
}

/**
 * Extends Parameter with semantics.
 */
export class SemanticParameter {

    constructor(
        // Underlying parameter
        public readonly parameter: Parameter,
        // Component parameters if this is a tuple.
        public readonly components: Optional<SemanticParameters>,
        // If this parameter should be excluded from the resulting dataset.
        public readonly exclude: boolean,
        // Any optional transformations to apply to the parameter
        public readonly transform: Optional<SemanticParameterTransform>
    ) { }

    get name(): string {
        return this.parameter.name;
    }

    /**
     * Return the parameter at the given path or empty if invalid.
     */
    getAt(pathParts: string[]): Either<SemanticAbiValidationError, SemanticParameter>  {
        // see if there are components to traverse
        return this.components.map(c => c.getAt(pathParts))
            // nothing to traverse if no components
            .getOr(new Left(new SemanticAbiValidationError(`Parameter "${this.parameter.name}" has no components.`)));
    }

    validate(): Optional<SemanticAbiValidationError> {
        if (this.parameter instanceof TupleParameter && this.transform.isPresent) {
            return Optional.of(new SemanticAbiValidationError('Transforms are not supported for tuples'));
        }
    }

    static fromJSON(parameter: Parameter, parameterJson: SemanticParameterJson): SemanticParameter {
        return new SemanticParameter(
            parameter,
            Optional.ofType(parameter, TupleParameter)
                .map(p => SemanticParameters.fromParameters(p.components, parameterJson['components'])),
            parameterJson['@exclude'] || false,
            Optional.of(parameterJson['@transform']).map(t => SemanticParameterTransform.fromJSON(t))
        );
    }

}

