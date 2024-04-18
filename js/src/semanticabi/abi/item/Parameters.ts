import {Parameter, PrimitiveParameter, TupleParameter} from "semanticabi/abi/item/Parameter";
import {InvalidAbiError} from "semanticabi/abi/InvalidAbiError";

/**
 * List of input or output parameters in an event or function, or components of a tuple parameter
 *
 * @author zuyezheng
 */
export class Parameters {

    constructor(
        private readonly _parameters: Parameter[]
    ) { }

    parameters(indexed?: boolean): Parameter[] {
        if (indexed === undefined) {
            return this._parameters;
        }
        return this._parameters.filter(e => e.isIndexed === indexed);
    }

    /**
     * Return an array of signatures for each parameter optionally filtering out indexed parameters.
     */
    signatures(indexed?: boolean): string[] {
        return this.parameters(indexed).map(e => e.signature);
    }

    /**
     * Deserialize parameters from JSON.
     */
    static fromJSON(jsonElements: ParameterJson[]): Parameters {
        return new Parameters(Parameters.parametersFromJson(jsonElements));
    }

    /**
     * Recursively parse out parameters to account for tuples/structs.
     */
    private static parametersFromJson(parameterJsons: ParameterJson[]): Parameter[] {
        const parameters: Parameter[] = [];
        for (const parameterJson of parameterJsons) {
            const parameterName = parameterJson['name'];
            if (parameterName === '') {
                throw new InvalidAbiError('Parameter name cannot be empty.');
            }
            const parameterType = parameterJson['type'];

            if (['tuple', 'tuple[]', 'tuple[][]'].includes(parameterType)) {
                parameters.push(new TupleParameter(
                    parameterName,
                    parameterJson['indexed'] === true,
                    parameterType.endsWith('[]'),
                    parameterType.endsWith('[][]'),
                    Parameters.parametersFromJson(parameterJson['components'])
                ));
            } else {
                parameters.push(new PrimitiveParameter(
                    parameterName,
                    parameterJson['indexed'] === true,
                    parameterType
                ));
            }
        }
        return parameters;
    }

}

export interface ParameterJson {

    name: string;
    type: string;
    indexed?: boolean;
    components?: ParameterJson[];

    [key: string]: any;

}
