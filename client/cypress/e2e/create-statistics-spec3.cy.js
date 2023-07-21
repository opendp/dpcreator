{
    describe('Create Statistics Wizard Step tests', () => {
        before(() => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()
            cy.createAccount('oscar', 'oscar@sesame.com', 'oscar123!')
            cy.logout()

        })
        beforeEach(() => {
            cy.loadTeacherSurveyDemo()
        })
        afterEach(() => {
            cy.logout()
        })
        //TODO: uncomment when analysis is ready
/*
        it('Displays Fixed Value Input Correctly', () => {
            let variables = {
                "age": {
                    "name": "age",
                    "label": "age",
                    "type": "Integer",
                    "min": "20",
                    "max": "75"
                },
            }
            cy.get('[data-test="Add Statistic"]').click({force: true});
            cy.get('[data-test="AddStatisticDialog"]').should('be.visible')
            // The fixed input field should be visible after switching from Count to Mean
            cy.get('[data-test="Count"]').click({force: true});
            cy.get('[data-test="age"]').click({force: true})
            cy.get('[data-test="Fixed value"]').should('not.exist')
                cy.get('[data-test="Mean"]').click({force: true});
                cy.get('[data-test="Fixed value"]').should('exist')
                cy.get('[data-test="Count"]').click({force: true});
                cy.get('[data-test="Fixed value"]').should('not.exist')

                cy.get('[data-test="Create Statistic Button"]').click({force: true})
                // The statistic should have been created
                cy.get('tr').first().get('td').should('contain', "Count")

                cy.get('[data-test="Add Statistic"]').click({force: true});
                cy.get('[data-test="AddStatisticDialog"]').should('be.visible')
                cy.get('[data-test="Mean"]').click({force: true});
            cy.get('[data-test="Fixed value"]').should('be.visible')
            cy.get('[data-test="age"]').click({force: true})

                // The fixed input should be required to Create the  Statistic if it's visible
            cy.get('[data-test="Create Statistic Button"]').should('be.disabled')
            cy.get('[data-test="Fixed value"]').type('35')
            cy.get('[data-test="Create Statistic Button"]').should('be.enabled')
                cy.get('[data-test="Create Statistic Button"]').click({force: true})
                // The statistic should have been created
                cy.get('tr').first().get('td').should('contain', "Mean")


        })

*/
    })
}