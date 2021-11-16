module.exports = {
   mode: 'jit',
   purge: [
      './pages/**/*.js',
      './components/**/*.js'
   ],
   theme: {
      extend: {
         fontFamily: {
            'sans': 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial'
         },
         colors: {
            "nhsuk-text": "#212b32",
            "nhsuk-secondary-text": "#4c6272",
            "nhsuk-link": "#005eb8",
            "nhsuk-link-hover": "#7C2855",
            "nhsuk-link-visited": "#330072",
            "nhsuk-link-active": "#002f5c",
            "nhsuk-focus": "#ffeb3b",
            "nhsuk-focus-text": "#212b32",
            "nhsuk-border": "#d8dde0",
            "nhsuk-form-border": "#4c6272",
            "nhsuk-error": "#d5281b",
            "nhsuk-button": "#007f3b",
            "nhsuk-secondary-button": "#4c6272",
            "nhsuk-blue": "#005eb8",
            "nhsuk-green": "'#007f3b'",
            "nhsuk-yellow": "#ffeb3b",
            "nhsuk-warm-yellow": "#ffb81C",
            "nhsuk-red": "#d5281b",
            "nhsuk-dark-pink": "#7C2855",
            "nhsuk-purple": "#330072",
            "nhsuk-grey-1": "#4c6272",
            "nhsuk-grey-2": "#768692",
            "nhsuk-grey-3": "#aeb7bd",
            "nhsuk-grey-4": "#d8dde0",
            "nhsuk-grey-5": "#f0f4f5",
            "nhsuk-white": "#ffffff",
            "nhsuk-pale-yellow": "#fff9c4",
            'blue': {
               '50': '#f2f7fb',
               '100': '#e6eff8',
               '200': '#bfd7ed',
               '300': '#99bfe3',
               '400': '#4d8ecd',
               '500': '#005eb8',
               '600': '#0055a6',
               '700': '#00478a',
               '800': '#00386e',
               '900': '#002e5a'
            },
            'green': {
               '50': '#f2f9f5',
               '100': '#e6f2eb',
               '200': '#bfdfce',
               '300': '#99ccb1',
               '400': '#4da576',
               '500': '#007f3b',
               '600': '#007235',
               '700': '#005f2c',
               '800': '#004c23',
               '900': '#003e1d'
            },
            'gray': {
               '50': '#f6f7f8',
               '100': '#edeff1',
               '200': '#d2d8dc',
               '300': '#b7c0c7',
               '400': '#82919c',
               '500': '#4c6272',
               '600': '#445867',
               '700': '#394a56',
               '800': '#2e3b44',
               '900': '#253038'
            }
         },
         typography: {
            DEFAULT: {
               css: {
                  pre: {
                     background: '#edeff1',
                     color: '#212b32',
                     padding: '2rem',
                     borderRadius: '0px',
                     whiteSpace: 'pre-line'
                  },
                  p: {
                     color: '#212b32'
                  },
                  th: {
                     fontSize: '16px'
                  },
                  td: {
                     fontSize: '16px'
                  }
               },
            },
         }
      }
   },
   variants: {},
   plugins: [
      require('@tailwindcss/typography'),
      require('@tailwindcss/forms')
   ],
}