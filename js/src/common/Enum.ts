export type EnumGettable<E extends Enum> = {get: (name: string) => E}

/**
 * Enum with built-in support for name to enum lookups and ordinals.
 *
 * @author zuyezheng
 */
export abstract class Enum {

    static NAME_TO_ENUM: Map<string, Enum>;

    static finalize() {
        this.NAME_TO_ENUM = new Map();
        let ordinal = 0;
        for (let prop in this) {
            if (this.hasOwnProperty(prop)) {
                // @ts-ignore
                const enumInstance: Enum = this[prop];
                if (enumInstance instanceof this) {
                    enumInstance._ordinal = ordinal++;
                    this.NAME_TO_ENUM.set(enumInstance.name, enumInstance);
                }
            }
        }
    }

    static names(): string[] {
        return Array.from(this.NAME_TO_ENUM.keys());
    }

    static enums<T extends Enum>(): T[] {
        return <T[]>Array.from(this.NAME_TO_ENUM.values());
    }

    static get<T extends Enum>(name: string): T | null {
        return <T>this.NAME_TO_ENUM.get(name);
    }

    protected _ordinal: number;

    protected constructor(public readonly name: string) { }

    public get ordinal(): number {
        return this._ordinal;
    }

    toString(): string {
        return this.name;
    }

    toJSON(): string {
        return this.name;
    }

}