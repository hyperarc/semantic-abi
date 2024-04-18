module.exports = {
    preset: 'ts-jest',
    testEnvironment: 'node',
    transformIgnorePatterns: ["node_modules"],
    transform: {
        '^.+\\.ts$': 'ts-jest',
    },
    testRegex: "\\S+/test/\\S+.test\\.ts$",
    moduleNameMapper: {
        '^@test/(.*)$': '<rootDir>/test/$1'
    },
    modulePaths: [
        "<rootDir>/src",
        "<rootDir>/node_modules"
    ],
    reporters: ["default", "jest-junit"]
};