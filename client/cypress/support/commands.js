Cypress.Commands.add('login', (email, password) => {
    cy.visit('/log-in')
    cy.get('[data-test="username"]').type('dev_admin');
    cy.get('[data-test="password"]').type('admin');
    cy.get('[data-test="Log in"]').click();

    // This test is necessary to prevent cypress from canceling the
    // the POST to login to  the server (right now, login redirects to the welcome page)
    cy.url().should('contain', 'welcome')

})
// Not using this,
// but keeping the code here as an example for future tests using Vuex store
Cypress.Commands.add('storeExample', (email, password) => {
    const getStore = () => cy.window().its('app.$store')
    cy.visit('/')
    getStore().then(store => {
        store.dispatch('login', email, password)
    })
    getStore().its('state.auth.user').should('deep.equal', 'dev_admin')


})


//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
