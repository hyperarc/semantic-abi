import {Enum} from "common/Enum";

/**
 * Supported EVM chains.
 *
 * @author zuyezheng
 */
export class EvmChain extends Enum {

    // Since Ethereum is a base coin rather than a token, it does not have a contract address like erc20 tokens, so we
    // create a sentinel address.
    static readonly ETHEREUM = new EvmChain('ethereum', '0x1111111111111111111111111111111111111111', true);

    static readonly ARBITRUM = new this('arbitrum', '0x1111111111111111111111111111111111111111', true);
    // AVAX address on the c-chain.
    static readonly AVALANCHE_C = new EvmChain('avalanche_c', '0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7', true);
    static readonly BASE = new EvmChain('base', '0x1111111111111111111111111111111111111111', true);
    static readonly BNB = new EvmChain('bnb', '0xb8c77482e45f1f44de1745f52c74426c631bdd52');
    static readonly OPTIMISM = new EvmChain('optimism', '0x1111111111111111111111111111111111111111', true);
    // Polygon networks use matic from polygon-pos chain.
    static readonly POLYGON = new EvmChain('polygon', '0x0000000000000000000000000000000000001010', true);
    static readonly POLYGON_ZKEVM = new EvmChain('polygon_zkevm', '0x0000000000000000000000000000000000001010');
    // TRX is a base coin in its blockchain without a contract address, therefore needs it own sentinel address
    static readonly TRON = new EvmChain('tron', '0x2222222222222222222222222222222222222222');
    static readonly ZKSYNC_ERA = new EvmChain('zksync_era', '0x1111111111111111111111111111111111111111');

    // Stability chains are technically feeless, so we just use a sentinel address.
    static readonly STABILITY = new EvmChain('stability', '0x1111111111111111111111111111111111111111');
    static readonly STABILITY_TESTNET = new EvmChain('stability_testnet', '0x1111111111111111111111111111111111111111');

    constructor(
        name: string,
        public readonly nativeTokenAddress: string,
        public readonly proxyCallSupported: boolean = false
    ) {
        super(name);
    }

    /**
     * Return all chains where HyperArc API supports proxy calls.
     */
    static proxyCallSupported(): EvmChain[] {
        return EvmChain.enums<EvmChain>().filter(chain => chain.proxyCallSupported);
    }

}
EvmChain.finalize();