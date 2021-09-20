{
    describe('Validate Dataset Page', () => {
        it('successfully saves Dataset questions', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()
            cy.createMockDataset('mockDV.json')
            // click on the start Process button on the welcome page,
            // to navigate to the Validate Dataset step of the Wizard
            cy.get('[data-test="Start Process"]').click();
            cy.url().should('contain', 'wizard')
            cy.get('[data-test="radioPrivateInformationYes"]').check({force: true})
            cy.get('[data-test="notHarmButConfidential"]').check({force: true})
            cy.get('[data-test="radioOnlyOneIndividualPerRowYes"]').check({force: true})

            // Go back to the Welcome page and start again, we should be back on the first step of the Wizard,
            // and the data should be saved:
            cy.visit('welcome')
            cy.get('[data-test="Start Process"]').click();
            cy.get('[data-test="radioPrivateInformationYes"]').should('be.checked').and('have.value', 'yes')
            cy.get('[data-test="notHarmButConfidential"]').should('be.checked').and('have.value', 'notHarmButConfidential')
            cy.get('[data-test="radioOnlyOneIndividualPerRowYes"]').should('be.checked').and('have.value', 'yes')
        })
    })
}