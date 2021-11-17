Cypress.Commands.add('createAccount', (username, email, password) => {
    cy.url().should('contain', 'sign-up')

    cy.get('h2').should('contain', '1/2. Check and accept Terms of Use:').should('be.visible')
    cy.get('[data-test="signupTermsCheckbox"]').click({force: true});
    cy.get('[data-test="continue"]').click({force: true});
    cy.get('[data-test="username"]').type(username);
    cy.get('[data-test="email"]').type(email);
    cy.get('[data-test="password"]').type(password);
    cy.get('[data-test="confirmPassword"').type(password)
    cy.get('[data-test="submit"]').click({force: true});
    cy.url().should('contains', 'confirmation')
})