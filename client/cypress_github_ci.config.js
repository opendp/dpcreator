module.exports = defineConfig({
  projectId: "8we926",
  defaultCommandTimeout: 100000,
  pageLoadTimeout: 100000,
  video: true,
  e2e: {
    // We've imported your old cypress plugins here.
    // You may want to clean this up later by importing these.
    setupNodeEvents(on, config) {
      return require('./cypress/plugins/index.js')(on, config)
    },
    baseUrl: 'http://server:8000',
  },
})
