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
            cy.goToConfirmVariables()
            cy.fixture('variables').then((varsFixture) => {
                for (const key in varsFixture) {
                    cy.get('table').contains('td', varsFixture[key].name).should('be.visible')
                    cy.get('table').contains('tr', varsFixture[key].name).should('contain', varsFixture[key].type)
                }
            })
        })
    })
}