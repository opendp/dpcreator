const {defineConfig} = require('cypress')

module.exports = defineConfig({
  projectId: "8we926",
  defaultCommandTimeout: 120000,
  pageLoadTimeout: 120000,
  video: true,
  e2e: {
    // We've imported your old cypress plugins here.
    // You may want to clean this up later by importing these.
    setupNodeEvents(on, config) {
      return require('./cypress/plugins/index.js')(on, config)
    },
    baseUrl: 'http://localhost:8000',
  },
})
