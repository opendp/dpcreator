{
    describe('Confirm Epsilon Page', () => {

        it('displays the page correctly', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.on("window:before:load", (win) => {
                //  cy.spy(win.console, "log");
                cy.spy(win.console, "error")
            })
            cy.clearData()
            let testFile = 'teacher_survey.csv'
            let testPath = 'cypress/fixtures/'+testFile
            let username = 'oscar'
            cy.createAccount(username, 'oscar@sesame.com', 'oscar123!')
            cy.uploadFile(testPath)
            cy.fixture('TeacherDemoData.json').then((demoData) => {
                cy.url().should('contain', 'my-data')
                cy.goToConfirmVariables(demoData)

                // select the variables we will use
                cy.selectVariable(demoData)
                cy.pause()
                cy.get('[data-test="wizardContinueButton"]').click()
                cy.get('h1').should('contain', 'Confirm Epsilon')
                cy.get('[data-test="wizardCompleteButton"]').should('be.enabled')
                cy.get('[data-test="confirmEpsilon"]').clear().type('5')
                cy.get('[data-test="wizardCompleteButton"]').should('be.disabled')
                cy.get('[data-test="confirmEpsilon"]').clear().type('.85')
                cy.get('[data-test="wizardCompleteButton"]').should('be.enabled')
                cy.get('[data-test="wizardCompleteButton"]').click()
                cy.url().should('contain', 'my-data')
                cy.get('tr').should('contain.text', '.85')
            })
        })
    })
}