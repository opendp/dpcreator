{
    describe('My Analysis Plans Page', () => {
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
                cy.fixture('analysisPlansDatasetList.json').then(dataset => {
                    // set Expiration Date and Time Remaining
                    analysisPlanList.plans.map(plan =>{
                        const millisInDay = 1000 * 60 * 60 * 24
                        const millisInHour = 1000 * 60 * 60
                        const millisInMin = 1000 * 60
                        const createdDate = new Date()
                        const expirationDate = createdDate.getTime() + (3 * millisInDay)
                        const diffTime = expirationDate - createdDate
                        const diffDays = Math.floor(diffTime / (millisInDay))
                        const diffHours = Math.floor((diffTime - (diffDays * millisInDay)) / millisInHour)
                        const diffMin = Math.floor((diffTime - (diffDays * millisInDay + diffHours * millisInHour)) / millisInMin)
                        const timeRemaining= '' + diffDays + 'd ' + diffHours + 'h ' + diffMin + 'min'
                        plan.timeRemaining = timeRemaining
                        plan.expirationDate = expirationDate

                    })
                       cy.intercept('GET', '/api/dataset-info/', {
                        body: {
                            "count": 1,
                            "next": null,
                            "previous": null,
                            "results": [dataset]
                        }
                    })
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
    })
}