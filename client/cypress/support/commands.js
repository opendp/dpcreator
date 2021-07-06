Cypress.Commands.add('login', (email, password) => {
    cy.visit('/log-in')
    cy.get('[data-test="username"]').type(email);
    cy.get('[data-test="password"]').type(password);
    cy.get('[data-test="Log in"]').click();

    // This test is necessary to prevent cypress from canceling the
    // the POST to login to  the server (right now, login redirects to the welcome page)
    cy.url().should('contain', 'welcome')

})
Cypress.Commands.add('clearData', () => {
    cy.login('dev_admin', 'admin')
    cy.request('/cypress-tests/clear-test-data/')
})

// TODO - replace this with data from a fixture
Cypress.Commands.add('createMockDataset', () => {
    cy.visit('/mock-dv');
    cy.get('[data-test="submit button"]').click();
    cy.url().should('contains', '/?id=');
    cy.scrollTo("bottom");
    cy.get('[data-test="termsOfServiceCheckbox"]').click({force: true});

    // This get (below) is more readable, but it causes a cypress error saying that the element
    // is detachached from the DOM.  Need to investigate further, but in the meantime, use the less
    // readable get string.
    //    cy.get('[data-test="loginButton"]').click({multiple:true});
    cy.get('#account-buttons--placeholder .v-btn--is-elevated > .v-btn__content').click()
    cy.url().should('contain', 'log-in')
    // The login command triggers the creation of a dataverse file from the mockdv form
    cy.login('dev_admin', 'admin')

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
