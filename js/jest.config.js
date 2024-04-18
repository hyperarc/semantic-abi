module.exports = {
    preset: 'ts-jest',
    testEnvironment: 'node',
    transformIgnorePatterns: ["node_modules"],
    transform: {
        '^.+\\.ts$': 'ts-jest',
    },
    testRegex: "\\S+/test/\\S+.test\\.ts$",
    modulePaths: [
        "<rootDir>/src",
        "<rootDir>",
        "<rootDir>/node_modules"
    ],
    reporters: ["default", "jest-junit"],
    moduleNameMapper: {}
};