{
    describe('Create Statistics Wizard Step tests', () => {

        beforeEach(() => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()
            cy.login('dev_admin', 'admin')
            cy.fixture('datasetInfoStep600.json').then(dataset => {
                dataset.created = '' + new Date()
                dataset.depositorSetupInfo.updated = dataset.created
                cy.intercept('GET', '/api/dataset-info/' + dataset.objectId + '/', {body: dataset})
                cy.intercept('GET', '/api/dataset-info/', {
                    body: {
                        "count": 1,
                        "next": null,
                        "previous": null,
                        "results": [dataset]
                    }
                })
                cy.fixture('analysisPlanStep700.json').then(analysisPlan => {
                    cy.intercept('GET', '/api/analyze/' + analysisPlan.objectId + '/', {body: analysisPlan})
                })
                cy.visit('/my-data')
                cy.get('tr').should('contain',
                    'Replication Data for: Eye-typing experiment')
                cy.get('[data-test="continueWorkflow"]').click({force: true})
            })
        })

        it('Goes to the correct wizard step', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.get('h1').should('contain', 'Create the statistics')
        })
        it('Contains correct variables in the Add Statistics dialog ', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.fixture('variables').then((varsFixture) => {
                // Create your statistic
                cy.get('[data-test="Add Statistic"]').click({force: true});
                for (const key in varsFixture) {
                    cy.get('label').should('contain', varsFixture[key].name)
                }
                cy.get('[data-test="Mean"]').click({force: true});
                for (const key in varsFixture) {
                    if (varsFixture[key].type !== 'Numerical') {
                        cy.get('label').should('not.contain', varsFixture[key].name)
                    }
                }
            })
        })

    })
}