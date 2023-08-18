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

            cy.get('h1').should('contain', 'Dataset')
            cy.get('h1').should('contain',
                'PUMS5extract1000.csv')

        })


    })
}