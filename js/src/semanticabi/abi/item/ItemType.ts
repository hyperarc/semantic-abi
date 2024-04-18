import {Enum} from "common/Enum";

export class ItemType extends Enum {

    static readonly EVENT = new this('event', false);
    static readonly FUNCTION = new this('function', true);
    static readonly CONSTRUCTOR = new this('constructor', true);
    static readonly FALLBACK = new this('fallback', true);
    static readonly RECEIVE = new this('receive', true);
    static readonly ERROR = new this('error', false);

    constructor(name: string, isFunction: boolean) {
        super(name);
    }

}
ItemType.finalize();