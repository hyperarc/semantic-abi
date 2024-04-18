import {ParameterJson, Parameters} from "semanticabi/abi/item/Parameters";
import {JsonObject} from "common/CommonTypes";
import Web3 from "web3";


/**
 * Standard ABI Event or Function.
 *
 * @author zuyezheng
 */
export abstract class AbiItem {

    // need a client to access the decoding stuff
    protected static readonly WEB3 = new Web3('http://foo.bar');

    public readonly signature: string;

    protected constructor(
        public readonly name: string,
        public readonly inputs: Parameters,
        public readonly extra: JsonObject
    ) {
        this.name = name;
        this.inputs = inputs;
        this.extra = extra;

        this.signature = `${this.name}(${this.inputs.signatures().join(",")})`;
    }

    abstract get hash(): string;

}

export type AbiItemJson = {

    name: string,
    type: string,
    anonymous?: boolean,
    inputs: ParameterJson[],
    outputs?: ParameterJson[]
    extra?: JsonObject

    [key: string]: any;

}