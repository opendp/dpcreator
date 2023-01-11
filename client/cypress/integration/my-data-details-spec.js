{
    describe('My Data Details Page', () => {
        beforeEach(() => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()
            const username = 'kermit'
            const email = 'kermit@thefrog.com'
            const password = 'kermit123!'

            cy.createAccount(username, email, password)
            let testfile = 'cypress/fixtures/PUMS5extract1000.csv'
            cy.uploadFile(testfile)
            cy.visit('/my-data')
            cy.get('tr').should('contain',
                'PUMS5extract1000.csv')
            cy.get('tr').should('contain',
                'Uploaded')
            cy.get('[data-test="viewDetails"]').click({force: true});
        })
        it('successfully loads', () => {
            cy.url().should('contain', 'my-data-details')

            cy.get('h1').should('contain', 'Data File')
            cy.get('h1').should('contain',
                'PUMS5extract1000.csv')

        })
        it('handles delete action', () => {
            // Test Cancel Delete
            cy.get('[data-test="delete"]').should('be.visible')
            cy.get('[data-test="delete"]').click({force: true})
            cy.get('[data-test="deleteDatasetCancel"]').click({force: true})
            cy.url().should('contain', 'my-data-details')
            cy.get('h1').should('contain', 'Data File')
            cy.get('h1').should('contain',
                'PUMS5extract1000.csv')

            // Test Confirm Delete
            cy.get('[data-test="delete"]').click({force: true})
            cy.get('[data-test="deleteDatasetConfirm"]').click({force: true})
            cy.url().should('contain', 'my-data')
            cy.get('tr').should('not.contain',
                'PUMS5extract1000.csv')
            // click to my-profile, then back to my-data page and make sure the dataset is still removed
            cy.visit('/my-profile')
            cy.get('h2').should('contain', 'Edit account information').should('be.visible')
            cy.visit('/my-data')

            cy.get('tr').should('not.contain',
                'PUMS5extract1000.csv')


        })

    })
}