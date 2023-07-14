{
    describe('Create Account Test', () => {
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
            cy.logout()

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
            cy.vuex().its('state.auth.user').should('exist')
            cy.vuex().its('state.auth.user.handoffId').should('be.null')

        })

    })
}