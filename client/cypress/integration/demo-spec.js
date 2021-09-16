{
    describe('Confirm Variables Page', () => {

        beforeEach(() => {
            cy.on("window:before:load", (win) => {
                cy.spy(win.console, "log");
                cy.spy(win.console, "error")
            })
        })
        it('uses the test Dataverse', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()
            cy.createMockDataset('dataverseMockDV.json')
            cy.url().should('contain', 'welcome')
            cy.get('.soft_primary.rounded-lg.mt-10.pa-16').should('contain',
                ' Teacher Climate Survey ')


        })
    })
}