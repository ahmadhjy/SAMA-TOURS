// Compile with Tailwind 3.4.17; do not run the CDN compiler in production.
module.exports = {
      darkMode: 'class', content: ['./templates/website/flight_match.html', './website/flight_match_copy.py', './static/js/flight_match.js'],
      theme: {
        extend: {
          colors: {
            brand: {
              navy: '#0B1B3D',
              deep: '#061024',
              royal: '#1E56A0',
              accent: '#2A69AC',
              gold: '#D4AF37',
              goldHover: '#BF9B27',
              goldLight: '#FDF6E2',
              whish: '#E60028',
              omtYellow: '#FFCC00',
              omtDark: '#1A1A1A'
            }
          },
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
            arabic: ['Cairo', 'sans-serif']
          }
        }
      }
    , important: '#sama-match-page', corePlugins: { preflight: false } };
