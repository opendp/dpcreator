{
    describe('Create Account Test', () => {
        it('Creates a Dataverse user with Handoff', () => {
            Cypress.Cookies.debug(true)
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)

                return false
            })
            cy.clearData()
            const username = 'kermit'
            const email = 'kermit@thefrog.com'
            const password = 'kermit123!'
            cy.visit('/mock-dv');
            cy.get('[data-test="submit button"]').click();
            cy.url().should('contains', '/?id=');
            cy.scrollTo("bottom");
            cy.get('[data-test="termsOfServiceCheckbox"]').click({force: true});
            cy.get('[data-test="createAccountButton"]').click({force: true, multiple: true});
            cy.url().should('contain', 'sign-up')
            cy.createAccount(username, email, password)
            cy.get('[data-test="My Profile"]').click();
            cy.url().should('contains', 'my-profile')
            cy.get('h2').should('contain', 'Edit account information').should('be.visible')
            cy.get('[data-test="myProfileUsername"]').should('have.value', username)


        })
        it('Shows error message if user name is taken', () => {
            cy.clearData()
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)

                return false
            })
            const username = 'oscar'
            const email = 'oscar@thegrouch.com'
            const password = 'oscar123!'
            cy.createAccount(username, email, password).then(() => {
                const waitForConfirmation = false
                cy.createAccount(username, email, password, waitForConfirmation)
                cy.get('[data-test="errorMessage"]').contains('A user with that username already exists.')
            })


        })
        it('Creates an OpenDP user with no Handoff', () => {
            cy.clearData()
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)

                return false
            })
            const username = 'oscar'
            const email = 'oscar@thegrouch.com'
            const password = 'oscar123!'
            cy.createAccount(username, email, password)
            cy.get('[data-test="My Profile"]').click();
            cy.get('h2').should('contain', 'Edit account information').should('be.visible')
            cy.get('[data-test="myProfileUsername"]').should('have.value', username)
        })

    })
}