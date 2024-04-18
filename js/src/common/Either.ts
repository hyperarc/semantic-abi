import {Optional} from "common/Optional";

/**
 * Scala-esque either. Left bad, right good.
 *
 * @author zuyezheng
 */
export interface Either<L, R> {

    get isLeft(): boolean;

    get isRight(): boolean;

    forEach(f: (v: R) => void): void;

    forEachAndSwap(f: (v: R) => void): Either<R, L>;

    map<R1>(f: (v: R) => R1): Either<L, R1>;

    flatMap<R1>(f: (v: R) => Either<L, R1>): Either<L, R1>;

    /**
     * Execute f if this is a right and swap with result. Just swap if left.
     */
    mapAndSwap<R1>(f: (v: R) => R1): Either<R1, L>;

    swap(): Either<R, L>;

    match<R1, L1>(rF: (v: R) => R1, lF: (v: L) => L1): Either<L1, R1>;

    fold<C>(rF: (v: R) => C, lF: (v: L) => C): C;

    /**
     * Return the right value or throw an exception with the left with an optional custom function.
     */
    rightOrThrow(errorF?: (l: L) => Error): R;

    /**
     * Turn a left into none and a right into some.
     */
    optional(): Optional<R>;

}

export class Left<L, R> implements Either<L, R> {

    constructor(
        public readonly value: L
    ) {}

    get isLeft(): boolean {
        return true;
    }

    get isRight(): boolean {
        return false;
    }

    forEach(f: (v: R) => void): void {
        // nothing to do
    }

    forEachAndSwap(f: (v: R) => void): Either<R, L> {
        return this.swap();
    }

    map<R1>(f: (v: R) => R1): Either<L, R1> {
        return new Left(this.value);
    }

    flatMap<R1>(f: (v: R) => Either<L, R1>): Either<L, R1> {
        return new Left(this.value);
    }

    mapAndSwap<R1>(f: (v: R) => R1): Either<R1, L> {
        // nothing to do, just swap
        return new Right(this.value);
    }

    swap(): Either<R, L> {
        return new Right(this.value);
    }

    match<R1, L1>(rF: (v: R) => R1, lF: (v: L) => L1): Either<L1, R1> {
        return new Left(lF(this.value));
    }

    fold<C>(rF: (v: R) => C, lF: (v: L) => C): C {
        return lF(this.value);
    }

    rightOrThrow(errorF?: (l: L) => Error): R {
        throw errorF == null ? new Error(this.value.toString()) : errorF(this.value);
    }

    optional(): Optional<R> {
        return Optional.none();
    }

}

export class Right<L, R> implements Either<L, R> {

    constructor(
        public readonly value: R
    ) {}

    get isLeft(): boolean {
        return false;
    }

    get isRight(): boolean {
        return true;
    }

    forEach(f: (v: R) => void): void {
        f(this.value);
    }

    forEachAndSwap(f: (v: R) => void): Either<R, L> {
        this.forEach(f);
        return this.swap();
    }

    map<R1>(f: (v: R) => R1): Either<L, R1> {
        return new Right(f(this.value));
    }

    flatMap<R1>(f: (v: R) => Either<L, R1>): Either<L, R1> {
        return f(this.value);
    }

    mapAndSwap<R1>(f: (v: R) => R1): Either<R1, L> {
        return new Left(f(this.value));
    }

    swap(): Either<R, L> {
        return new Left(this.value);
    }

    match<R1, L1>(rF: (v: R) => R1, lF: (v: L) => L1): Either<L1, R1> {
        return new Right(rF(this.value));
    }

    fold<C>(rF: (v: R) => C, lF: (v: L) => C): C {
        return rF(this.value);
    }

    rightOrThrow(throwF?: (l: L) => void): R {
        return this.value;
    }

    optional(): Optional<R> {
        return Optional.some(this.value);
    }

}