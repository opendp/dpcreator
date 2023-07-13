{
    beforeEach(() => {
        cy.on('uncaught:exception', (e, runnable) => {
            console.log('error', e)
            console.log('runnable', runnable)
            return false
        })
        cy.clearData()


    })
    describe('Validate Dataset Page', () => {
        it('successfully saves Dataset questions', () => {
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
            // click on the start Process button on the welcome page,
            // to navigate to the Validate Dataset step of the Wizard
            cy.get('[data-test="continueWorkflow"]').click({force: true})
            cy.pause()
            cy.url().should('contain', 'wizard')
            cy.get('[data-test="radioPrivateInformationYes"]').check({force: true})
            cy.get('[data-test="notHarmButConfidential"]').check({force: true})
            cy.get('[data-test="radioOnlyOneIndividualPerRowYes"]').check({force: true})
            cy.get('[data-test="Larger Population - yes"]').click({force: true})

            cy.get('[data-test="populationSizeInput"]').clear().type('0')
            cy.get('div').should('contain', 'Population size must greater than 0')
            cy.get('[data-test="populationSizeInput"]').clear()
            cy.get('[data-test="populationSizeInput"]').type('200')
            cy.get('div').should('not.contain', 'Population size must greater than sample size')
            // Go back to the Welcome page and start again, we should be back on the first step of the Wizard,
            // and the data should be saved:


            cy.visit('/my-data')
            cy.get('[data-test="continueWorkflow"]').click({force: true})
            cy.get('[data-test="radioPrivateInformationYes"]').should('be.checked').and('have.value', 'yes')
            cy.get('[data-test="notHarmButConfidential"]').should('be.checked').and('have.value', 'notHarmButConfidential')
            cy.get('[data-test="radioOnlyOneIndividualPerRowYes"]').should('be.checked').and('have.value', 'yes')
        })
    })
}