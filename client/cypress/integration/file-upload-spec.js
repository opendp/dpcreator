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
        it('Handles Invalid File format', () => {
            let testfile = 'cypress/fixtures/invalidspss.sav'
            cy.uploadFile(testfile)
            cy.wizardStepOne()
            // click on continue to go to trigger the profiler and go to the Confirm Variables Page
            cy.get('[data-test="wizardContinueButton"]').last().click({force: true});
            // Confirm Variables page should show profiler error message.
            cy.get('div').should('contain', 'File reading error.')
            cy.pause()
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