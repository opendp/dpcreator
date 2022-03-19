{
    describe('Create Statistics Wizard Step tests', () => {

        beforeEach(() => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()

        })
        it('Displays Release Info and links', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })

            /*
            export properties then -
            curl -X DELETE -H  X-Dataverse-key:$API_TOKEN  "$SERVER_URL/api/access/datafile/$FILE_ID/auxiliary/$FORMAT_TAG/$FORMAT_VERSION"
             */
            cy.fixture('releaseDetailsAnalysisPlan.json').then(analysisPlan => {
                cy.intercept('GET', '/api/analyze/' + analysisPlan.objectId + '/', {body: analysisPlan})
            })
            cy.fixture('releaseDetailsDatasetInfo.json').then(dataset => {
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

                cy.createAccount('ernie', 'ernie@sesame.org', 'ernie123!')
                cy.visit('my-data')
                cy.get('[data-test="viewDetails"]').click({force: true});
                cy.url().should('contains', 'my-data-details')
                cy.get('[data-test="jsonDownload"]').should('be.visible')
                cy.get('[data-test="pdfDownload"]').should('not.exist')
            })

        })


    })
}