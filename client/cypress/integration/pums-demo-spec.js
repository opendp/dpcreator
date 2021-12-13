{
    describe('PUMS Demo Test', () => {

        beforeEach(() => {
            cy.on("window:before:load", (win) => {
                cy.spy(win.console, "log");
                cy.spy(win.console, "error")
            })
        })
        it('Uses the PUMS dataset', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.runDemo('PUMSMockDV.json', 'PUMSDemoData.json')
            // Test aux file already exists
            // logout
            // submit mock-dv form
            //login
            // welcome page shouldn't show "start Process"
            cy.logout()
            const createAccount = false
            cy.createMockDataset('PUMSMockDV.json', createAccount)
            cy.get('[data-test="Start Process"]').should('not.exist');


        })
        //   it("Doesn't show Start Process button if aux file is already deposited",() =>{
//
        //   })
    })
}