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

        it('removes buttons when time expired', () => {
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
            cy.uploadFile(testfile)

            cy.get('[data-test="continueWorkflow"]').should('be.visible')
            // timeout is 3 days, so set to a little more than that
            const millisInDay = 1000 * 60 * 60 * 24
            const currentTime = new Date().getTime()
            const testtime = (3 * millisInDay) + 600000
            cy.clock(currentTime + testtime)
            cy.visit('/my-data')
            cy.get('td').should('contain', 'Time has expired')
            cy.get('[data-test="viewDetails"]').should('not.exist')
            cy.get('[data-test="continueWorkflow"]').should('not.exist')


        })
        it('successfully loads', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)

                return false
            })
            cy.clearData()
            cy.createMockDataset('EyeDemoMockDV.json')
            cy.visit('/my-data')

            cy.get('tr').should('contain',
                'Replication Data for: Eye-typing experiment')
            cy.get('tr').should('contain',
                'Uploaded')
            cy.get('[data-test="continueWorkflow"]').click({force: true});
            cy.get('h1').should('contain', 'Validate Data File')

        })
        it('deletes dataset', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)

                return false
            })
            cy.clearData()
            cy.createMockDataset('EyeDemoMockDV.json')
            cy.visit('/my-data')

            cy.get('tr').should('contain',
                'Replication Data for: Eye-typing experiment')
            cy.get('tr').should('contain',
                'Uploaded')

            cy.get('[data-test="delete"]').click({force: true})
            cy.get('[data-test="deleteDatasetConfirm"]').click({force: true})

            cy.get('tr').should('not.contain',
                'Replication Data for: Eye-typing experiment')
            // click to my-profile, then back to my-data page and make sure the dataset is still removed
            cy.visit('/my-profile')
            cy.get('h2').should('contain', 'Edit account information').should('be.visible')
            cy.visit('/my-data')

            cy.get('tr').should('not.contain',
                'Replication Data for: Eye-typing experiment')


        })
        it('deletes dataset and analysis plan', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)

                return false
            })
            cy.clearData()
            const demoDatafile = 'EyeDemoStatsTest.json'
            const mockDVfile = 'EyeDemoMockDV.json'
            cy.createMockDataset(mockDVfile)
            cy.fixture(demoDatafile).then((demoData) => {
                cy.url().should('contain', 'welcome')
                cy.get('.soft_primary.rounded-lg.mt-10.pa-16').should('contain',
                    demoData['datasetName'])
                cy.goToConfirmVariables(demoData.variables)
                // select the variables we will use
                cy.selectVariable(demoData.variables)

                // Continue to Set Epsilon Step
                cy.epsilonStep()
                // Add all the statistics in the Create Statistics Step
                cy.createStatistics(demoData)

                cy.visit('/my-data')

                cy.get('tr').should('contain',
                    'Replication Data for: Eye-typing experiment')
                cy.get('tr').should('contain',
                    'In Progress')

                cy.get('[data-test="delete"]').click({force: true})
                cy.get('[data-test="deleteDatasetConfirm"]').click({force: true})
                cy.get('tr').should('not.contain',
                    'Replication Data for: Eye-typing experiment')
                // click to my-profile, then back to my-data page and make sure the dataset is still removed
                cy.visit('/my-profile')
                cy.get('h2').should('contain', 'Edit account information').should('be.visible')
                cy.visit('/my-data')

                cy.get('tr').should('not.contain',
                    'Replication Data for: Eye-typing experiment')


            })
        })

    })
}