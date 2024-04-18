import {JsonObject} from "common/CommonTypes";

/**
 * Decoded value that supports serialization back into json.
 *
 * @author zuyezheng
 */
export interface Decoded {

    /**
     * Add the decoding of the current object to the JSON object.
     */
    addToJson(jsonObj: JsonObject): JsonObject;

}