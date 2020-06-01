module.exports = {
    "env": {
        "commonjs": true,
        "es6": true,
        "node": true
    },
    "extends": "eslint:recommended",
    "globals": {
        "Atomics": "readonly",
        "SharedArrayBuffer": "readonly"
    },
    "parserOptions": {
        "ecmaVersion": 2018
    },
    "rules": {
        "curly": "off",
        "single": "off",
        "quotes": [1, "single", { "avoidEscape": true }],
        "no-console": "off",
        "semi": "warn",
        "eqeqeq": "warn"
    }
};