{
    describe('Confirm Variables Page', () => {
        it('displays the variables correctly', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()
            cy.createMockDataset('EyeDemoMockDV.json')
            cy.fixture('variables').then((varsFixture) => {
                cy.goToConfirmVariables(varsFixture)

                for (const key in varsFixture) {
                    cy.get('table').contains('td', varsFixture[key].name).should('be.visible')
                    cy.get('table').contains('tr', varsFixture[key].name).should('contain', varsFixture[key].type)
                }
                const label = 'Trial'
                const minInput = label + ':min'
                const maxInput = label + ':max'
                cy.get('[data-test="wizardContinueButton"]').should('be.disabled')
                cy.contains('td', label).parent('tr').children().first().click()
                cy.get('[data-test="' + minInput + '"]').type('0');
                cy.get('[data-test="' + maxInput + '"]').type('100');
                cy.get('[data-test="' + maxInput + '"]').should('have.value', 100)
                cy.get('[data-test="' + maxInput + '"]').trigger('change')
                cy.contains('td', 'Session').parent('tr').children().first().click()

                cy.get('[data-test="wizardContinueButton"]').should('not.be.disabled')


            })
        })
    })
}