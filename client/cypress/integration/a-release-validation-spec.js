{
    describe('Test EyeHeight statistic', () => {

        beforeEach(() => {
            cy.on("window:before:load", (win) => {
                cy.spy(win.console, "log");
                cy.spy(win.console, "error")
            })
        })

        it('Validates EyeHeight Mean ', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })

            cy.runDemo('mockDV.json', 'fatigueData.json')


        })
    })
}