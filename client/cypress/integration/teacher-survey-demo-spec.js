{
    describe('Demo Test', () => {

        beforeEach(() => {
            cy.on("window:before:load", (win) => {
                cy.spy(win.console, "log");
                cy.spy(win.console, "error")
            })
        })
        it('Uses the Teacher Survey', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.runDemo('TeacherSurveyMockDV.json', 'TeacherSurveyDemoData.json')
        })
    })
}