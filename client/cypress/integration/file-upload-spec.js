{
    describe('File Upload Test', () => {
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

        })
        it('Uploads file with select input', () => {
            let testfile = 'cypress/fixtures/PUMS5extract1000.csv'
            cy.uploadFile(testfile)

        })
        it('Uploads file with drag drop', () => {

            cy.get('[data-test="My Data"]').click();
            cy.url().should('contains', 'my-data')
            cy.get('[data-test="myDataUploadButton"]').click();

            cy.get('[data-test="dragArea"]').selectFile('cypress/fixtures/FultonPUMS5full.csv',
                {force: true, action: 'drag-drop'})
            cy.get('tr').should('contain',
                'FultonPUMS5full.csv')
            cy.get('tr').should('contain',
                'Uploaded')

        })
    })
}