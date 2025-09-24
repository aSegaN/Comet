// frontend/eslint.config.mjs
import js from '@eslint/js';
import { FlatCompat } from '@eslint/eslintrc';
import { fileURLToPath } from 'url';
import path from 'path';

// __dirname en ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Compat pour résoudre "next/core-web-vitals"
const compat = new FlatCompat({ baseDirectory: __dirname });

export default [
  // 1) IGNORES GLOBAUX — DOIVENT ARRIVER EN PREMIER
  {
    ignores: [
      '.next/**',
      'node_modules/**',
      'dist/**',
      'out/**',
      'coverage/**'
    ],
  },

  // 2) Bases ESLint
  js.configs.recommended,

  // 3) Config officielle Next (équivalent "extends: ['next/core-web-vitals']")
  ...compat.extends('next/core-web-vitals'),

  // 4) Règles projet
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
    rules: {
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      // Si la règle import/no-anonymous-default-export gêne :
      // 'import/no-anonymous-default-export': 'off',
    },
  },
];
