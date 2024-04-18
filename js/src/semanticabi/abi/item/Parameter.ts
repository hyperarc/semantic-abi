/**
 * An input or output parameter in an event or function, or a component of a tuple parameter.
 *
 * @author zuyezheng
 */
export interface Parameter {

    get name(): string;

    get isIndexed(): boolean;

    get isArray(): boolean;

    get isArrayOfArrays(): boolean;

    get signature(): string;

}

/**
 * Parameter for primitive values like address, uint256, and strings.
 */
export class PrimitiveParameter implements Parameter {

    constructor(
        public readonly name: string,
        public readonly isIndexed: boolean,
        public readonly primitiveType: string
    ) { }

    get isArray(): boolean {
        return this.primitiveType.endsWith('[]');
    }

    get isArrayOfArrays(): boolean {
        return this.primitiveType.endsWith('[][]');
    }

    get signature(): string {
        return this.primitiveType;
    }
}

/**
 * "Tuple" (struct) parameter.
 */
export class TupleParameter implements Parameter {

    constructor(
        public readonly name: string,
        public readonly isIndexed: boolean,
        public readonly isArray: boolean,
        public readonly isArrayOfArrays: boolean,
        public readonly components: Parameter[]
    ) {
    }

    get signature(): string {
        let signature = `(${this.components.map(c => c.signature).join(',')})`;
        if (this.isArray) signature += '[]';
        if (this.isArrayOfArrays) signature += '[]';
        return signature;
    }

}