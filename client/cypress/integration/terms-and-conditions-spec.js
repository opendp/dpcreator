{
    describe('Terms and Conditions test', () => {
        it('goes to Terms and Conditions if current terms not accepted', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()
            // create account
            // login
            // get user objectId
            // logout
            // intercept terms of access, to trigger needing to accept terms
            // login again - should go to terms of access
            const username = 'bigbird'
            const email = 'bigbird@nest.com'
            const password = 'bigbird123!'
            cy.createAccount(username, email, password)
            cy.login(username, password).then(() => {
                console.log(sessionStorage)
                const sessionObj = JSON.parse(sessionStorage.getItem('vuex'))
                const userObjectId = sessionObj.auth.user.objectId
                // simulate the user having excepted older terms of use
                cy.intercept('GET', '/api/terms-of-access-agreement/', {
                    body: {
                        "count": 1, "next": null, "previous": null,
                        "results": [{"user": userObjectId, "terms_of_access": "old-object-id"}]
                    }
                })
                cy.logout()
                cy.login(username, password)
                cy.url().should('contains', 'terms')
            })


        }),
            it('goes directly to My Data page when terms are already accepted', () => {
                cy.on('uncaught:exception', (e, runnable) => {
                    console.log('error', e)
                    console.log('runnable', runnable)
                    return false
                })
                cy.clearData()
                // create account
                // login
                // get user objectId and current terms Id
                // logout
                // intercept terms of access, to simulate user already excepted terms
                // login again - should go to my-data

                const username = 'bigbird'
                const email = 'bigbird@nest.com'
                const password = 'bigbird123!'
                cy.createAccount(username, email, password)

                cy.login(username, password).then(() => {
                    console.log(sessionStorage)
                    const sessionObj = JSON.parse(sessionStorage.getItem('vuex'))
                    const userObjectId = sessionObj.auth.user.objectId
                    const currentTermsId = sessionObj.auth.currentTerms.objectId
                    // simulate the user having already accepted current terms of use
                    cy.intercept('GET', '/api/terms-of-access-agreement/', {
                        body: {
                            "count": 1, "next": null, "previous": null,
                            "results": [{"user": userObjectId, "terms_of_access": currentTermsId}]
                        }
                    })
                    cy.logout()
                    cy.login(username, password)
                    cy.url().should('contains', 'my-data')
                })

            })
    })
}
