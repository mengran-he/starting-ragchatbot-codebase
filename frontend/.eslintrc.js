module.exports = {
    env: {
        browser: true,
        es2021: true,
    },
    extends: ['eslint:recommended'],
    parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'script',
    },
    globals: {
        marked: 'readonly',
    },
    rules: {
        'no-unused-vars': 'warn',
        'no-console': 'off',
        eqeqeq: ['error', 'always'],
        curly: ['error', 'all'],
        'no-var': 'error',
        'prefer-const': 'error',
        'no-trailing-spaces': 'error',
        'no-multiple-empty-lines': ['error', { max: 1, maxEOF: 0 }],
        quotes: ['error', 'single'],
        semi: ['error', 'always'],
    },
};
