{
    describe('My Data Page', () => {
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
    })
}