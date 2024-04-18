/**
 * Scala-esque optional.
 *
 * @author zuyezheng
 */
export class Optional<T> {

    static none<T>(): Optional<T> {
        return new Optional<T>(null);
    }

    static some<T>(value: T): Optional<T> {
        return new Optional<T>(value);
    }

    static of<T>(value: T | null): Optional<T> {
        return value == null ? Optional.none() : Optional.some(value);
    }

    /**
     * Treat nulls and empty strings as none.
     */
    static string(s: string | null): Optional<string> {
        return s ? Optional.some(s) : Optional.none();
    }

    /**
     * Converts a boolean to optional semantics, true will become Some and false will be None.
     */
    static bool(b: boolean): Optional<boolean> {
        return b ? Optional.some(b) : Optional.none();
    }

    static ofType<T>(value: any, clazz: abstract new (...args: any[]) => T): Optional<T> {
        if (value instanceof clazz) {
            return Optional.some<T>(value);
        } else {
            return Optional.none();
        }
    }

    /**
     * Map a function that returns T or null into an Optional.
     */
    static map<T>(f: () => T | null): Optional<T> {
        return Optional.of(f());
    }

    /**
     * Resolve to some when all optionals are present.
     */
    static all(optionals: Optional<any>[]): Optional<any[]> {
        const values = [];
        for (let o of optionals) {
            if (o.isNone) {
                return Optional.none();
            } else {
                values.push(o.get());
            }
        }

        return Optional.some(values);
    }

    /**
     * Return the first non-empty optional or none.
     */
    static any(optionals: Optional<any>[]): Optional<any> {
        return optionals.reduce((a, b) => a.orElse(() => b));
    }

    constructor(public readonly value: T) { }

    get isPresent(): boolean {
        return this.value != null;
    }

    get isNone(): boolean {
        return this.value == null;
    }

    map<T1>(f: (v: T) => T1): Optional<T1> {
        if (this.isPresent) {
            return Optional.some(f(this.value));
        } else {
            return Optional.none();
        }
    }

    /**
     * Like map, but f can return a null which will be flattened to None or an optional which will be passed through.
     */
    flatMap<T1>(f: (v: T) => T1 | null | Optional<T1>): Optional<T1> {
        if (this.isPresent) {
            const v = f(this.value);
            return v instanceof Optional ? v : Optional.of(v);
        } else {
            return Optional.none();
        }
    }

    match<T1>(fSome: (v: T) => T1, fNone: () => T1): T1 {
        if (this.isPresent) {
            return fSome(this.value);
        } else {
            return fNone();
        }
    }

    /**
     * Do something if not none.
     */
    forEach(f: (v: T) => void): Optional<T> {
        if (this.isPresent) {
            f(this.value);
        }

        return this;
    }

    /**
     * Do something if none.
     */
    orForEach(f: () => void): Optional<T> {
        if (this.isNone) {
            f();
        }

        return this;
    }

    /**
     * Apply the filter and map to None if it is false or the original optional otherwise.
     */
    filter(f: (v: T) => boolean): Optional<T> {
        if (this.isPresent && f(this.value)) {
            return this;
        } else {
            return Optional.none();
        }
    }

    /**
     * Return a new optional if none.
     */
    orElse(f: () => Optional<T>): Optional<T> {
        if (this.isNone) {
            return f();
        }

        return this;
    }

    getOrElse(f: () => T): T {
        if (this.isPresent) {
            return this.value;
        } else {
            return f();
        }
    }

    get(): T {
        if (this.isPresent) {
            return this.value;
        } else {
            throw new Error('Optional is none.');
        }
    }

    getOr(other: T): T {
        if (this.isPresent) {
            return this.value;
        } else {
            return other;
        }
    }

    get nullable(): T | null | undefined {
        return this.value;
    }

    /**
     * Turn false into none.
     */
    get bool(): Optional<boolean> {
        return Optional.bool(this.value === true);
    }

    /**
     * Return an array of the current value or empty array if none.
     */
    get array(): T[] {
        if (this.isPresent) {
            return [this.value];
        } else {
            return [];
        }
    }

}