Cypress.Commands.add('login', (email, password) => {
    Cypress.Cookies.debug(true)
    cy.visit('/log-in')
    cy.get('[data-test="username"]').type(email);
    cy.get('[data-test="password"]').type(password);
    cy.get('[data-test="Log in"]').click();
    // to force the login click, test that the browser went to the next  page
    cy.url().should('not.contain', 'log-in')

})
Cypress.Commands.add('clearData', () => {
    cy.login('dev_admin', 'admin')
    cy.request('/cypress-tests/clear-test-data/')


})

Cypress.Commands.add('vuex', () =>
    cy.window()
        .its('app.$store')
)


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
    cy.get('[data-test="username"]').type('dev_admin');
    cy.get('[data-test="password"]').type('admin');
    cy.get('[data-test="Log in"]').click();
    // first we will be routed to the Terms of Conditions page for the user
    cy.get('[data-test="confirmTermsCheckbox"]').click({force: true});
    cy.get('[data-test="confirmTermsContinue"]').click();
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
