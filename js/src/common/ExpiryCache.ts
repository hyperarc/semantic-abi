import {OrderedMap} from "common/OrderedMap";
import {Tuple} from "common/Tuple";
import {Optional} from "common/Optional";

/**
 * Cache with time based expiration as well as LRU eviction.
 *
 * @author zuyezheng
 */
export class ExpiryCache<K, V> {

    private cache: OrderedMap<K, Tuple<V, number>>;

    constructor(
        private readonly cacheSize: number,
        // invalidate query cache at 10 minutes by default
        private readonly defaultTimeoutMilli: number
    ) {
        this.cache = OrderedMap.empty();
    }

    /**
     * Return the entry for the key if cached and not expired.
     */
    get(key: K): Optional<V> {
        return this.cache.get(key).flatMap(v => Date.now() > v.right ? null : v.left);
    }

    /**
     * Return the entry for the key if cached and not expired, or execute f to add and entry for the key.
     */
    getOr(key: K, f: () => V, timeoutMilli?: number): V {
        return this.get(key).getOrElse(() => {
            return this.add(key, f(), timeoutMilli);
        });
    }

    /**
     * Delete the entry for the key, returning an optional of what was deleted.
     */
    delete(key: K): Optional<V> {
        return this.cache.delete(key).map(v => v.left);
    }

    /**
     * Purge the cache of expired entries, returning anything that might've been purged.
     */
    purge(): V[] {
        // remove anything that might have timed out
        const now = Date.now();
        const keysToPurge = this.cache.keys.flatMap(
            k => this.cache.get(k).get().right < now ? [k] : []
        );
        const purged = keysToPurge.map(k => this.cache.delete(k).get().left);

        // purge LRU to maintain cache size
        while (this.cache.size > this.cacheSize) {
            purged.push(this.cache.popFirst().get().left);
        }

        return purged;
    }

    /**
     * Add something to the cache.
     */
    add(key: K, value: V, timeoutMilli?: number): V {
        this.cache.set(
            key, Tuple.of(value, Date.now() + (timeoutMilli || this.defaultTimeoutMilli))
        );
        this.purge();
        return value;
    }

}