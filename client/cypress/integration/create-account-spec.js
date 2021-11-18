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
            cy.url().should('contains', 'confirmation')
            // We have turned off email confirmation for Cypress, so we should be able
            // to log in now with the new account.
            cy.visit('/log-in')
            cy.get('[data-test="username"]').type(username);
            cy.get('[data-test="password"]').type(password);
            cy.get('[data-test="Log in"]').click();
            cy.url().should('contains', 'welcome')
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
            cy.visit('/sign-up')
            cy.createAccount(username, email, password).then(() => {
                cy.url().should('contains', 'confirmation')
                cy.visit('/sign-up')
                cy.createAccount(username, email, password)
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
            cy.visit('/sign-up')
            cy.createAccount(username, email, password)
            cy.url().should('contains', 'confirmation')
            cy.visit('/log-in')
            cy.get('[data-test="username"]').type(username);
            cy.get('[data-test="password"]').type(password);
            cy.get('[data-test="Log in"]').click();
            cy.get('[data-test="My Profile"]').click();
            cy.get('h2').should('contain', 'Edit account information').should('be.visible')
            cy.get('[data-test="myProfileUsername"]').should('have.value', username)
        })

    })
}