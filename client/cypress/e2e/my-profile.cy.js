{
    describe('My Profile Page', () => {
        it('updates account details', () => {
            Cypress.Cookies.debug(true)
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)

                return false
            })
            cy.clearData()
            const username = 'kermit'
            const newUsername = 'kermie'
            const email = 'kermit@thefrog.com'
            const newEmail = 'kermit@harvard.edu'
            const password = 'kermit123!'
            cy.visit('/')
            cy.createAccount(username, email, password)

            cy.get('[data-test="My Profile"]').click();
            cy.url().should('contains', 'my-profile')
            cy.get('h2').should('contain', 'Edit account information').should('be.visible')
            cy.get('[data-test="myProfileUsername"]').should('be.visible').should('have.value', username)
            cy.get('[data-test="myProfileEmail"]').should('be.visible').should('have.value', email)
            cy.get('[data-test="myProfileUsername"]').clear()
            cy.get('[data-test="myProfileUsername"]').type(newUsername)
            cy.get('[data-test="myProfileEmail"]').clear()
            cy.get('[data-test="myProfileEmail"]').type(newEmail)
            cy.get('[data-test="myProfileSaveChanges"]').click()
            cy.get('div').should('contain', 'Profile has been changed')

            cy.get('[data-test="changedUserName"]').should('contain', newUsername)
            cy.get('[data-test="changedEmail"]').should('contain', newEmail)
            cy.get('[data-test="homeLogo"]').click()
            cy.url().should('not.contain', 'my-profile')
            cy.get('[data-test="My Profile"]').click()
            cy.get('[data-test="myProfileUsername"]').should('be.visible').should('have.value', newUsername)
            cy.get('[data-test="myProfileEmail"]').should('be.visible').should('have.value', newEmail)

        })

    })
}