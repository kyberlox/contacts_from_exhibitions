module.exports = {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'theme-grey-blue': '#5f7686',
                'theme-blue-light': '#20baff',
                'theme-blue-dark': '#015db4',
                'theme-black': '#000000',
                'theme-orange': '#f3990f',
                'theme-row-background-gray': '#f7f7f7',
            },
        },
    },
    plugins: [],
}