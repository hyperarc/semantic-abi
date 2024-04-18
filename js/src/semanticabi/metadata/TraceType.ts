import {Enum} from "common/Enum";

export class TraceType extends Enum {

    static readonly CALL = new this('call');
    static readonly REWARD = new this('reward');

}
TraceType.finalize();
