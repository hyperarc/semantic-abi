import {Optional} from "common/Optional";
import { Tuple } from "common/Tuple";

/**
 * ES6 maps are documented to retain insertion order, but replacement of an element does not maintain order and puts it
 * in the back. This strictly maintains insertion order even with replacement with specific semantics for add and
 * replace. It also has some nice helpers such as getting the first or last element which don't exist on map.
 *
 * @author zuyezheng
 */
export class OrderedMap<K, V> {

    static fromKeyed<K, V>(vs: V[], fk: (v: V) => K): OrderedMap<K, V> {
        return new OrderedMap<K, V>(
            new Map(vs.map(v => [fk(v), v]))
        );
    }

    static empty<K, V>(): OrderedMap<K, V> {
        return new OrderedMap<K, V>(new Map());
    }

    private _keys: K[];

    public constructor(
        private readonly _map: Map<K, V>
    ) {
        this._keys = Array.from(_map.keys());
    }

    get size(): number {
        return this._keys.length;
    }

    get first(): V {
        return this._map.get(this._keys[0]);
    }

    get last(): V {
        return this._map.get(this._keys[this.size - 1]);
    }

    public map<T>(f: (v: V, i: number, k: K) => T): T[] {
        return this._keys.map(
            (k: K, i: number) => f(this._map.get(k), i, k)
        );
    }

    /**
     * Find the last key before the given key, returning last if not found and None if it is the first.
     */
    lastBefore(k: K): Optional<K> {
        const index = this._keys.indexOf(k);
        if (index === -1) {
            return Optional.some(this._keys[this._keys.length - 1]);
        } else if (index === 0) {
            return Optional.none();
        } else {
            return Optional.some(this._keys[index - 1]);
        }
    }

    get keys(): K[] {
        return this._keys;
    }

    get values(): V[] {
        return this._keys.map(k => this._map.get(k));
    }

    has(k: K): boolean {
        return this._map.has(k);
    }

    get(k: K): Optional<V> {
        return Optional.of(this._map.get(k));
    }

    at(i: number): V {
        return this._map.get(this._keys[i]);
    }

    /**
     * Like get but also return the index of the found key.
     */
    find(k: K): Optional<Tuple<V, number>> {
        const index = this._keys.indexOf(k);
        if (index >= 0) {
            return Optional.some(Tuple.of(this._map.get(k), index));
        } else {
            return Optional.none();
        }
    }

    /**
     * Try to add an item returning an Optional of none if added or the existing value if it already exists and no
     * operation performed.
     */
    add(k: K, v: V): Optional<V> {
        if (this._map.has(k)) {
            return Optional.some(this._map.get(k));
        }

        this._keys.push(k);
        this._map.set(k, v);

        return Optional.none();
    }

    /**
     * Set the value for the key regardless of if it already exists, setting will always change the order of the key to
     * the end. Return the value that might have been replaced.
     */
    set(k: K, v: V): Optional<V> {
        const prior = this.delete(k);
        this.add(k, v);

        return prior;
    }

    /**
     * Try to replace an item in place, returning what was replaced. If the key doesn't exist, the item will not be
     * inserted and none returned.
     *
     * Optionally specify a new key to replace the old while keeping the ordering.
     */
    replace(k: K, v: V, newK?: K): Optional<V> {
        const toReplace = this._map.get(k);
        if (toReplace == null) {
            return Optional.none();
        }

        if (newK == null || newK === k) {
            // if no new key or it's the same as the original, just replace
            this._map.set(k, v);
        } else {
            this._keys = this._keys.map(curK => curK === k ? newK : curK);
            this._map.delete(k);
            this._map.set(newK, v);
        }

        return Optional.some(toReplace);
    }

    /**
     * Try to delete an item, returning what was deleted. If the key doesn't exist, return none.
     */
    delete(k: K): Optional<V> {
        const toDelete = this._map.get(k);
        if (toDelete == null) {
            return Optional.none();
        }

        this._keys = this._keys.filter(curK => curK !== k);
        this._map.delete(k);
        return Optional.some(toDelete);
    }

    /**
     * Pop the earliest value added.
     */
    popFirst(): Optional<V> {
        if (this.size === 0) {
            return Optional.none();
        }

        return this.delete(this._keys[0]);
    }

    /**
     * Shallow copy.
     */
    copy(): OrderedMap<K, V> {
        return new OrderedMap<K, V>(new Map(this._map));
    }

    /**
     * Since JSON doesn't make any assertions about ordering of maps, return this as an array by default.
     */
    toJSON(): Object {
        return this.values;
    }
}
