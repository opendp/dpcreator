{
    describe('My Data Page', () => {
        beforeEach(() => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()


        })

        it('displays Table correctly', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)

                return false
            })
            let testfile = 'cypress/fixtures/PUMS5extract1000.csv'
            const username = 'kermit'
            const email = 'kermit@thefrog.com'
            const password = 'kermit123!'

            cy.createAccount(username, email, password)
            cy.fixture('analysisPlanList.json').then(analysisPlanList => {

                cy.intercept('GET', '/api/analyze/', {
                    body: {
                        "count": 1,
                        "next": null,
                        "previous": null,
                        "results": analysisPlanList.plans
                    }
                })
                cy.visit('/my-plans')

                cy.get('[data-test="my-plans-table"]').should('be.visible')
                analysisPlanList.plans.forEach(plan => {
                    cy.get('[data-test="my-plans-table"]').should('contain.text', plan.datasetName)
                })
            })

        })

    })
}