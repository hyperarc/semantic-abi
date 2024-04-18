import {Optional} from "common/Optional";

/**
 * A stack with a max number of items, after max is reached, the oldest in the stack will be dropped.
 */
export class BoundedStack<T> {

    private readonly _values: T[];

    constructor(public readonly max: number) {
        this._values = [];
    }

    get values(): T[] {
        return this._values.slice();
    }

    /**
     * Push a new item and return the item removed if any.
     */
    push(value: T): Optional<T> {
        this._values.push(value);
        if (this._values.length > this.max) {
            return Optional.some(this._values.shift());
        } else {
            return Optional.none();
        }
    }

    /**
     * Pop the top item if any.
     */
    pop(): Optional<T> {
        if (this.isEmpty()) {
            return Optional.none();
        }

        return Optional.some(this._values.pop());
    }

    /**
     * Remove and return all items.
     */
    clear(): T[] {
        return this._values.splice(0);
    }

    isEmpty(): boolean {
        return this._values.length === 0;
    }

    get length(): number {
        return this._values.length;
    }
}