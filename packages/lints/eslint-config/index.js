export default [
    {
        rules: {
            // Best practices
            "no-console": "warn",
            "no-debugger": "error",
            "no-unused-vars": ["warn", { 
                "argsIgnorePattern": "^_",
                "varsIgnorePattern": "^_" 
            }],
            
            // Code quality
            "prefer-const": "warn",
            "no-var": "error",
            "eqeqeq": ["warn", "always"],
            
            // React best practices
            "react/jsx-uses-react": "off",
            "react/react-in-jsx-scope": "off",
        }
    }
];
