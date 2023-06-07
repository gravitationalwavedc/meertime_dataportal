module.exports = {
  env: { browser: true, es2020: true, es2022: true },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react/jsx-runtime',
    'plugin:react-hooks/recommended',
    'prettier'
  ],
  overrides: [
    { files: ['**/*.cjs'], env: { node: true } },
    {
      files: ["**/*.test.js", "**/*.test.jsx", "**/*.test.ts", "**/*.test.tsx", "**/*.cy.js"],
      rules: {
        "react/prop-types": 0,
        "react/display-name": 0
      },
      globals: {
        cy: true,
        suite: true,
        test: true,
        describe: true,
        it: true,
        expect: true,
        assert: true,
        vitest: true,
        vi: true,
        beforeAll: true,
        afterAll: true,
        beforeEach: true,
        afterEach: true
      }
    }
  ],
  parserOptions: { ecmaVersion: "latest", sourceType: 'module' },
  settings: { react: { version: '18.2' } },
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': 'warn'
  }
}
