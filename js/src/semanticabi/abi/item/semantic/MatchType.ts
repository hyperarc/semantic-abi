import {Enum} from "common/Enum";

/**
 * The type of data we are matching for.
 */
export class MatchType extends Enum {

    // Match an event.
    static readonly EVENT = new this('event');
    // Match a function.
    static readonly FUNCTION = new this('function');
    // Special type to match against a transfer-type of event that has a fromAddress, toAddress, and value.
    static readonly TRANSFER = new this('transfer');

}
MatchType.finalize();
