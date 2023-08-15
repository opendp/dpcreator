{
    describe('Confirm Variables Validation tests', () => {

        beforeEach(() => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()
            cy.setupConfirmVariablesPage('datasetInfoStep400.json')

        })
        it('Uses fixtures on confirm Variables page', () => {

            cy.get('h1').should('contain', 'Confirm Variables')

        })

        it(' validates type integer', () => {

            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            const label = 'Trial'
            const minInput = label + ':min'
            const maxInput = label + ':max'
            //  selecting a numeric variable with min/max - test continue button
            cy.get('[data-test="wizardCompleteButton"]').should('be.disabled')
            cy.contains('td', label).parent('tr').children().first().click()
            cy.get('[data-test="' + minInput + '"]').type('0');
            cy.get('[data-test="' + maxInput + '"]').type('100');
            cy.get('[data-test="' + maxInput + '"]').should('have.value', 100)
            cy.get('[data-test="' + maxInput + '"]').trigger('change')
            cy.get('[data-test="wizardCompleteButton"]').should('not.be.disabled')


        })
        it(' validates type boolean', () => {

            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            const booleanLabel = 'Session'
            const trueValue = booleanLabel + ':trueValue'
            const falseValue = booleanLabel + ':falseValue'

            // Select boolean variable without additional information - continueButton should be disabled
            cy.contains('td', booleanLabel).parent('tr').children().first().click()
            cy.get('[data-test="wizardCompleteButton"]').should('be.disabled')

            // leave falseValue blank- continueButton should be disabled
            cy.get('[data-test="' + trueValue + '"]').type('1');
            cy.get('[data-test="wizardCompleteButton"]').should('be.disabled')

            // leave use same value for both fields - continueButton should be disabled
            cy.get('[data-test="' + falseValue + '"]').type('1');
            cy.get('[data-test="wizardCompleteButton"]').should('be.disabled')

            // change true value - continueButton should be enabled
            cy.get('[data-test="' + trueValue + '"]').type('2');
            cy.get('[data-test="wizardCompleteButton"]').should('not.be.disabled')

        })


    })
}