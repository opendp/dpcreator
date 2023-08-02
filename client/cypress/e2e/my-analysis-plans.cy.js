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
        it('Goes To Confirm Variables Analyst step  (e2e test)', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })

            cy.clearData()
            let testFile = 'cypress/fixtures/Fatigue_data.csv'
            cy.createAccount('oscar', 'oscar@sesame.com', 'oscar123!')
            cy.uploadFile(testFile)
            const selectVariables =  {
                "typingSpeed": {
                    "max": 25,
                    "min": 10,
                    "name": "TypingSpeed",
                    "type": "Float",
                    "label": "TypingSpeed",
                    "selected": true,
                    "sortOrder": 5
                },
                "blinkDuration": {
                    "max": 35,
                    "min": 10,
                    "name": "BlinkDuration",
                    "type": "Float",
                    "label": "",
                    "sortOrder": 12
                }}
            cy.fixture('EyeDemoData.json').then((demoData) => {
                cy.url().should('contain', 'my-data')
                cy.goToConfirmVariables(selectVariables)
                // select the variables we will use
                cy.selectVariable(selectVariables)
                cy.get('[data-test="wizardCompleteButton"]').click({force:true})
                cy.url().should('contain','my-data')
                cy.visit('/my-plans')
                //createPlanButton
                cy.get('[data-test="createPlanButton"]').click({force:true})
                cy.get('[data-test="selectPlanDataset"]').click();

                // Find and click the desired dataset option within the dropdown

                cy.contains('Fatigue_data.csv').click();

                const myPlanName = 'my cypress test plan'
                const myDesc = 'my cypress test desc'
                cy.get('[data-test="selectPlanAnalyst"]').click()
                cy.contains('oscar').click();
                cy.get('[data-test="inputPlanName"]').type(myPlanName)
                cy.get('[data-test="inputPlanName"]').type(myDesc)
                cy.get('[data-test="inputPlanBudget"]').type('0.1')
                cy.get('[data-test="createPlanSubmitButton"]').click({force:true})
                cy.get('td').should('contain', 'Fatigue_data.csv')
                const continueTestId = 'continueWorkflow0'
                cy.get('[data-test="'+continueTestId+'"]').click({force: true})
                cy.url().should('contains','analyst-wizard')


            })
        })

        it('calls delete analysis plan API', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)

                return false
            })
            const username = 'kermit'
            const email = 'kermit@thefrog.com'
            const password = 'kermit123!'

            cy.createAccount(username, email, password)
            cy.fixture('analysisPlanList.json').then(analysisPlanList => {

                    // set Expiration Date and Time Remaining
                    analysisPlanList.plans.map(plan =>{
                        const millisInDay = 1000 * 60 * 60 * 24
                        const createdDate = new Date()
                        const expirationDate = new Date (createdDate.getTime() + (3 * millisInDay))
                        plan.expirationDate = expirationDate

                    })

                    cy.intercept('GET', '/api/analysis-plan/', {
                        body: {
                            "count": 1,
                            "next": null,
                            "previous": null,
                            "results": analysisPlanList.plans
                        }
                    })
                cy.intercept('DELETE', '/api/analysis-plan/'+ analysisPlanList.plans[0].objectId, {
                  statusCode: 200
                }).as('deletePlan')
                    cy.visit('/my-plans')

                    cy.get('[data-test="my-plans-table"]').should('be.visible')
                    analysisPlanList.plans.forEach(plan => {
                        cy.get('[data-test="my-plans-table"]').should('contain.text', plan.datasetName)
                    })
                const deleteId = 'delete0'
                cy.get('[data-test="'+deleteId+'"]').click({force: true})
                cy.get('[data-test="deleteAnalysisConfirm"]').click({force: true})
                cy.wait('@deletePlan').its('response.statusCode').should('eq', 200)
                cy.get('[data-test="my-plans-table"]').should('not.contain.text', analysisPlanList.plans[0].datasetName)
            })


        })
        it('displays Table correctly', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)

                return false
            })
            const username = 'kermit'
            const email = 'kermit@thefrog.com'
            const password = 'kermit123!'

            cy.createAccount(username, email, password)
            cy.fixture('analysisPlanList.json').then(analysisPlanList => {
                cy.fixture('analysisPlansDatasetList.json').then(dataset => {
                    // set Expiration Date and Time Remaining
                    analysisPlanList.plans.map(plan =>{
                        const millisInDay = 1000 * 60 * 60 * 24
                        const createdDate = new Date()
                        const expirationDate = createdDate.getTime() + (3 * millisInDay)
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
                    cy.intercept('GET', '/api/analysis-plan/', {
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
        it('creates new Analysis Plan (e2e test)', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })

            cy.clearData()
            let testFile = 'cypress/fixtures/Fatigue_data.csv'
            cy.createAccount('oscar', 'oscar@sesame.com', 'oscar123!')
            cy.uploadFile(testFile)
            const selectVariables =  {
                "typingSpeed": {
                    "max": 25,
                    "min": 10,
                    "name": "TypingSpeed",
                    "type": "Float",
                    "label": "TypingSpeed",
                    "selected": true,
                    "sortOrder": 5
                },
                "blinkDuration": {
                    "max": 35,
                    "min": 10,
                    "name": "BlinkDuration",
                    "type": "Float",
                    "label": "",
                    "sortOrder": 12
                }}
            cy.fixture('EyeDemoData.json').then((demoData) => {
                cy.url().should('contain', 'my-data')
                cy.goToConfirmVariables(selectVariables)
                // select the variables we will use
                cy.selectVariable(selectVariables)
                cy.get('[data-test="wizardCompleteButton"]').click({force:true})
                cy.url().should('contain','my-data')
                cy.visit('/my-plans')
                //createPlanButton
                cy.get('[data-test="createPlanButton"]').click({force:true})
                cy.get('[data-test="selectPlanDataset"]').click();

                // Find and click the desired dataset option within the dropdown

                cy.contains('Fatigue_data.csv').click();


                cy.get('[data-test="selectPlanAnalyst"]').click()
                cy.contains('oscar').click();
                cy.get('[data-test="inputPlanName"]').type('my cypress test plan')
                cy.get('[data-test="inputPlanName"]').type('my cypress test desc')
                cy.get('[data-test="inputPlanBudget"]').type('0.1')
                cy.get('[data-test="createPlanSubmitButton"]').click({force:true})
                cy.get('td').should('contain', 'Fatigue_data.csv')
                const millisInDay = 1000 * 60 * 60 * 24
                const createdDate = new Date()
                const expirationDate = new Date (createdDate.getTime() + (3 * millisInDay))

                const month = expirationDate.toLocaleDateString('UTC', { month: 'long' }); // 'July'
                const day = expirationDate.getDate(); // 23
                const year = expirationDate.getFullYear(); // 2023
                const formattedDate = `${month} ${day}, ${year}`
                cy.get('td').should('contain',formattedDate)

            })
        })
    })
}