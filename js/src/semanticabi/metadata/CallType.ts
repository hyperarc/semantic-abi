import {Enum} from "common/Enum";

export class CallType extends Enum {

    static readonly CALL = new this('call');
    static readonly DELEGATECALL = new this('delegatecall');
    static readonly STATICCALL = new this('staticcall');
    static readonly CALLCODE = new this('callcode');
    // erigon will always be create, while geth might be create or create2
    static readonly CREATE = new this('create');
    // https://ethereum.stackexchange.com/questions/101336/what-is-the-benefit-of-using-create2-to-create-a-smart-contract
    static readonly CREATE2 = new this('create2');

}
CallType.finalize();
