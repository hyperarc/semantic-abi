export type JsonObject = {[key: string]: any};

export type Json = JsonObject | JsonObject[];

export type JsonDeserializer<T> = { fromJSON: (json: Json) => T }