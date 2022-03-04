{
    describe('Duck Demo Test', () => {

        beforeEach(() => {
            cy.on("window:before:load", (win) => {
                cy.spy(win.console, "log");
                cy.spy(win.console, "error")
            })
        })
        it('Uses the Duck dataset', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.runDemo('DuckNewVarNamesMockDV.json', 'DuckNewVarNamesDemoData.json')


        })
        //   it("Doesn't show Start Process button if aux file is already deposited",() =>{
//
        //   })
    })
}