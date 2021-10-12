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
            cy.setupStatisticsPage('datasetInfoStep600.json', 'analysisPlanStep700.json')
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