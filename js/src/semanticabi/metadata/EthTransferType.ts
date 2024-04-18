import {Enum} from "common/Enum";

/**
 * @author zuyezheng
 */
export class EthTransferType extends Enum {

    static readonly PRIMARY = new this('primary');
    static readonly INTERNAL = new this('internal');
    static readonly REWARD = new this('reward');
    static readonly ERC = new this('erc');

}
EthTransferType.finalize();
