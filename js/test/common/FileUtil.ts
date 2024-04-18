import util from "util";
import zlib from "zlib";
import fs from "fs";

const gunzip = util.promisify(zlib.gunzip);

export class FileUtil {

    constructor(
        public readonly baseDir: string
    ) {
    }

    async loadZippedJson<T>(path: string): Promise<T> {
        const buffer = fs.readFileSync(this.baseDir + '/' + path);
        const decompressedBuffer = await gunzip(buffer);
        return JSON.parse(decompressedBuffer.toString());
    }

    loadJson<T>(path: string): T {
        return JSON.parse(fs.readFileSync(this.baseDir + '/' + path).toString());
    }

}