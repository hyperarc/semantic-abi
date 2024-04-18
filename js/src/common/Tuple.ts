/**
 * Typescript "tuples" end up as arrays where each value can be any of the types defined in the tuple. This makes it
 * explicit.
 */
export class Tuple<T1, T2> {

    static of<T1, T2>(left: T1, right: T2): Tuple<T1, T2> {
        return new Tuple(left, right);
    }

    constructor(
        public readonly left: T1,
        public readonly right: T2
    ) { }

    /**
     * const [a, b] = tuple.destruct;
     */
    get destruct(): [T1, T2] {
        return [this.left, this.right];
    }

}