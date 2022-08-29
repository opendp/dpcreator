{
    describe('Confirm Variables Page', () => {
        it('displays the correct number of rows', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()
            cy.createMockDataset('EyeDemoMockDV.json')
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
            cy.createMockDataset('EyeDemoMockDV.json')
            cy.fixture('variables').then((varsFixture) => {
                cy.goToConfirmVariables(varsFixture)
                cy.pause()
                for (const key in varsFixture) {
                    cy.get('table').contains('td', varsFixture[key].name).should('be.visible')
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
                const booleanLabel = 'Session'
                const minInput = label + ':min'
                const maxInput = label + ':max'
                //  selecting a numeric variable with min/max - test continue button
                cy.get('[data-test="wizardContinueButton"]').should('be.disabled')
                cy.contains('td', label).parent('tr').children().first().click()
                cy.get('[data-test="' + minInput + '"]').type('0');
                cy.get('[data-test="' + maxInput + '"]').type('100');
                cy.get('[data-test="' + maxInput + '"]').should('have.value', 100)
                cy.get('[data-test="' + maxInput + '"]').trigger('change')
                cy.contains('td', booleanLabel).parent('tr').children().first().click()
                cy.get('[data-test="wizardContinueButton"]').should('not.be.disabled')

                // change numeric type to Categorical without adding categories - continue button should be disabled
                cy.get('[data-test="' + label + ':selectToolTip' + '"]').type('Categorical', {force: true})
                cy.get('[data-test="wizardContinueButton"]').should('be.disabled')

                // uncheck the variable and continue button should be enabled
                cy.contains('td', label).parent('tr').children().first().click()
                cy.get('[data-test="wizardContinueButton"]').should('not.be.disabled')

                // uncheck the other variable, then continue should be disabled because no variables are selected
                cy.contains('td', booleanLabel).parent('tr').children().first().click()
                cy.get('[data-test="wizardContinueButton"]').should('be.disabled')


            })
        })

    })
}