{
    describe('My Data Page', () => {
        beforeEach(() => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()


        })


        it('successfully loads', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)

                return false
            })
            let testfile = 'cypress/fixtures/PUMS5extract1000.csv'
            const username = 'kermit'
            const email = 'kermit@thefrog.com'
            const password = 'kermit123!'

            cy.createAccount(username, email, password)
            cy.uploadFile(testfile)
            cy.visit('/my-data')

            cy.get('tr').should('contain',
                'PUMS5extract1000.csv')
            cy.get('tr').should('contain',
                'Uploaded')
            cy.get('[data-test="continueWorkflow"]').click({force: true});
            cy.get('h1').should('contain', 'Validate Data File')

        })
        it('deletes dataset', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)

                return false
            })
            let testfile = 'cypress/fixtures/PUMS5extract1000.csv'
            const username = 'kermit'
            const email = 'kermit@thefrog.com'
            const password = 'kermit123!'

            cy.createAccount(username, email, password)
            cy.uploadFile(testfile)
            cy.visit('/my-data')

            cy.get('tr').should('contain',
                'PUMS5extract1000.csv')
            cy.get('tr').should('contain',
                'Uploaded')

            cy.get('[data-test="delete"]').click({force: true})
            cy.get('[data-test="deleteDatasetConfirm"]').click({force: true})

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