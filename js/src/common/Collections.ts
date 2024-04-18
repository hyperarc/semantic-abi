/**
 * Zip 2 arrays up to the shortest length.
 */
export function zip<T, U>(array1: T[], array2: U[]): [T, U][] {
    const length = Math.min(array1.length, array2.length);

    const result: [T, U][] = [];
    for (let i = 0; i < length; i++) {
        result.push([array1[i], array2[i]]);
    }

    return result;
}

/**
 * Zip columnar arrays into rows.
 */
export function zipAll(arrays: any[][]): any[][] {
    // Math.min() returns Infinity so need to explicitly handle nothing to zip.
    if (arrays.length === 0) {
        return [];
    }

    const length = Math.min(...arrays.map(a => a.length));
    const result: any[][] = [];
    for (let i = 0; i < length; i++) {
        result.push(arrays.map(a => a[i]));
    }

    return result;
}