{
    describe('Confirm Variables Page', () => {
        it('displays the variables correctlys', () => {
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

            // click on continue to go to trigger the profiler and go to the Confirm Variables Page
            cy.get('[data-test="wizardContinueButton"]').last().click();
            cy.get('h1').should('contain', 'Confirm Variables')
            cy.fixture('variables').then((varsFixture) => {
                for (const key in varsFixture) {
                    cy.get('table').contains('td', varsFixture[key].name).should('be.visible')
                    cy.get('table').contains('tr', varsFixture[key].name).should('contain', varsFixture[key].type)
                }
            })
        })
    })
}