{
    describe('Confirm Variables Page', () => {

        beforeEach(() => {
            cy.on("window:before:load", (win) => {
                cy.spy(win.console, "log");
                cy.spy(win.console, "error")
            })
        })
        it('uses the test Dataverse', () => {
            cy.clearData()
            cy.createMockDataset('dataverseMockDV.json')


        })
    })
}