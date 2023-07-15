{
    describe('Confirm Variables Page', () => {

        it('displays the correct number of rows', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.on("window:before:load", (win) => {
                cy.spy(win.console, "log");
                cy.spy(win.console, "error")
            })
            cy.clearData()
            let testfile = 'cypress/fixtures/Fatigue_data.csv'
            cy.createAccount('oscar', 'oscar@sesame.com', 'oscar123!')
            cy.uploadFile(testfile)
            cy.fixture('variables').then((varsFixture) => {
                cy.goToConfirmVariables(varsFixture)
                cy.get('[data-test="variableRow"]').should('have.length', Object.keys(varsFixture).length)
                cy.get('[data-test="filterCheckBox"]').click({force: true})
                cy.get('[data-test="variableRow"]').should('not.exist')
            })
        })

        it('saves categories correctly', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()
            let testfile = 'cypress/fixtures/Fatigue_data.csv'
            cy.createAccount('oscar', 'oscar@sesame.com', 'oscar123!')
            cy.uploadFile(testfile)
            cy.fixture('variables').then((varsFixture) => {
                cy.goToConfirmVariables(varsFixture).then(() => {
                    for (const key in varsFixture) {
                        cy.get('table').contains('td', varsFixture[key].name).should('exist')
                        cy.get('table').contains('tr', varsFixture[key].name).should('contain', varsFixture[key].type)
                    }
                    const label = 'Subject'
                    const name = 'subject'
                    const catInput = label + ':categories'
                    const catDataTest = '[data-test="' + catInput + '"]'
                    cy.get(catDataTest).type(varsFixture[name].categories, {force: true})
                    varsFixture[name].categoryChips.forEach(category => {
                        cy.get('[data-test="categoryChip"]').should('contain', category)
                    })
                })
            })
        })

    })
}