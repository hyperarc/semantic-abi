import {Enum} from "common/Enum";

/**
 * Token types supported in transfers.
 *
 * @author zuyezheng
 */
export class EthTokenType extends Enum {

    static readonly ETH = new this('Eth', false);
    static readonly ERC20 = new this('Erc20', false);
    static readonly ERC721 = new this('Erc721', false);
    static readonly ERC1155 = new this('Erc1155', false);
    static readonly CRYPTO_PUNKS = new this('CryptoPunks', false);

    constructor(
        name: string,
        public readonly isNft: boolean
    ) {
        super(name);
    }

}