Cypress.Commands.add('login', (username, password) => {
    Cypress.Cookies.debug(true)
    cy.visit('/log-in')
    cy.get('[data-test="username"]').type(username);
    cy.get('[data-test="password"]').type(password);
    cy.get('[data-test="Log in"]').click();
    // to force the login click, test that the browser went to the next  page
    cy.url().should('not.contain', 'log-in')

})
Cypress.Commands.add('loginAPI', (username, password) => {
    cy.request('POST', '/rest-auth/login/', {username, password}).then((response) => {
        expect(response.body).to.have.property('username', 'dev_admin')
    })
})
Cypress.Commands.add('clearData', () => {
    cy.intercept('POST', 'rest-auth/login').as('login')
    cy.intercept('POST', 'rest-auth/logout').as('logout')
    cy.login('dev_admin', 'admin')
    cy.wait('@login')
    cy.request('/cypress-tests/clear-test-data/')
        .then(() => cy.logout())

})

Cypress.Commands.add('logout', () => {
    cy.visit('/')
    if (sessionStorage.getItem('vuex') !== null) {
        const sessionObj = JSON.parse(sessionStorage.getItem('vuex'))
        if (sessionObj.auth.user !== null) {
            cy.intercept('POST', 'rest-auth/logout').as('logout')
            cy.get('[data-test="Logout Link"]').click()
            cy.wait('@logout')
            cy.get('[data-test="My Profile"]').should('not.exist');
        }
    }
})

Cypress.Commands.add('vuex', () =>
    cy.window()
        .its('app.$store')
)

Cypress.Commands.add('runDemo', (mockDVfile, demoDatafile) => {
    cy.clearData()
    cy.createMockDataset(mockDVfile)
    cy.fixture(demoDatafile).then((demoData) => {
        cy.url().should('contain', 'welcome')
        cy.get('.soft_primary.rounded-lg.mt-10.pa-16').should('contain',
            demoData['datasetName'])
        cy.goToConfirmVariables(demoData.variables)
        // try to find one numerical variable
        let numericVar = null
        for (const key in demoData.variables) {
            if (demoData.variables[key].type === 'Float' || demoData.variables[key].type === 'Integer') {
                numericVar = demoData.variables[key]
            }
        }
        if (numericVar !== null) {
            cy.createMeanStatistic(numericVar)
            cy.submitMeanStatistic()
        }

    })

})


Cypress.Commands.add('createMockDataset', (fixture, createAccount = true) => {
    cy.fixture(fixture).then((mockForm) => {
        if (createAccount) {
            cy.createAccount(mockForm['user'], mockForm['email'], mockForm['password'])
            //      cy.pause()
            cy.logout()
            //      cy.pause()
        }
        cy.visit('/mock-dv');
        //   cy.pause()
        cy.get('[data-test="siteUrl"]').clear().type(mockForm['siteUrl'])
        cy.get('[data-test="token"]').clear().type(mockForm['token'])
        cy.get('[data-test="fileId"]').clear().type(mockForm['fileId'])
        cy.get('[data-test="filePid"]').clear().type(mockForm['filePid'])
        cy.get('[data-test="datasetPid"]').clear().type(mockForm['datasetPid'])

        cy.get('[data-test="submit button"]').click();
        cy.url().should('contains', '/?id=');
        cy.scrollTo("bottom");
        cy.get('[data-test="termsOfServiceCheckbox"]').click({force: true});

        // This get (below) is more readable, but it causes a cypress error saying that the element
        // is detachached from the DOM.  Need to investigate further, but in the meantime, use the less
        // readable get string.
        //    cy.get('[data-test="loginButton"]').click({multiple:true});
        cy.get('#account-buttons--placeholder .v-btn--is-elevated > .v-btn__content').click()
        cy.url().should('contain', 'log-in')
        cy.get('[data-test="username"]').type(mockForm['user']);
        cy.get('[data-test="password"]').type(mockForm['password']);
        cy.get('[data-test="Log in"]').click();
        cy.url().should('contain', 'welcome')
    })
})


// Not using this,
// but keeping the code here as an example for future tests using Vuex store
Cypress.Commands.add('storeExample', (email, password) => {
    const getStore = () => cy.window().its('app.$store')
    cy.visit('/')
    getStore().then(store => {
        store.dispatch('login', email, password)
    })
    getStore().its('state.auth.user').should('deep.equal', 'dev_admin')


})
Cypress.Commands.add('goToConfirmVariables', (variableData) => {
    // click on the start Process button on the welcome page,
    // to navigate to the Validate Dataset step of the Wizard
    cy.intercept('GET', '/api/dataset-info/**',).as(
        'datasetInfo'
    )
    cy.get('[data-test="Start Process"]').click();
    cy.url().should('contain', 'wizard')
    cy.get('[data-test="radioPrivateInformationYes"]').check({force: true})
    cy.get('[data-test="notHarmButConfidential"]').check({force: true})
    cy.get('[data-test="radioOnlyOneIndividualPerRowYes"]').check({force: true})

    // click on continue to go to trigger the profiler and go to the Confirm Variables Page
    cy.get('[data-test="wizardContinueButton"]').last().click({force: true});
    cy.wait('@datasetInfo')
    cy.get('h1').should('contain', 'Confirm Variables')
    for (const key in variableData) {
        const val = variableData[key]
        cy.get('table').contains('td', val.name).should('be.visible')
        cy.get('table').contains('tr', val.name).should('contain', val.type)
    }


})
Cypress.Commands.add('createMeanStatistic', (numericVar) => {
    cy.intercept('PATCH', '/api/deposit/**',).as(
        'patchDeposit'
    )
    cy.intercept('GET', '/api/dataset-info/**',).as(
        'datasetInfo'
    )
    const minDataTest = '[data-test="' + numericVar.name + ':min"]'
    const maxDataTest = '[data-test="' + numericVar.name + ':max"]'
    // Enter min and max for one numericVar so we can validate
    cy.contains('td', numericVar.name).parent('tr').children().first().click()
    cy.get(minDataTest).should('be.visible')
    cy.get(maxDataTest).should('be.visible')
    cy.get(minDataTest).type(numericVar.min, {force: true})
    cy.wait(500)
    cy.get(maxDataTest).type(numericVar.max, {force: true})
    // click back into min input, to trigger change event on max input
    cy.get(minDataTest).click()
    //  cy.wait('@patchDeposit', {timeout: 5000})

    // Continue to Set Epsilon Step
    cy.scrollTo('top')
    cy.get('[data-test="wizardContinueButton"]').last().click({force: true});
    cy.wait('@datasetInfo', {timeout: 5000})

    cy.get('h1').should('contain', 'Set Accuracy Level').should('be.visible')
    cy.get('[data-test="Larger Population - no"]').check({force: true})
    //  cy.get('[data-test="Public Observations - yes"]').should('be.visible')
    cy.get('[data-test="Public Observations - yes"]').check({force: true})


    // Continue to Create  Statistics Step
    cy.scrollTo('top')
    cy.get('[data-test="wizardContinueButton"]').last().click({force: true});
    cy.wait('@datasetInfo', {timeout: 5000})

    // On the statistics page, test edit statistics Params
    cy.get('h1').should('contain', 'Create Statistics').should('be.visible')
    cy.get('[data-test="editConfidenceIcon"]').click({force: true});
    cy.get('h2').should('contain', 'Are you sure you want to proceed?').should('be.visible')
    cy.get('[data-test="confirmButton"]').click({force: true});

    cy.get('[data-test="editEpsilonInput"]').should('have.value', 1)
    cy.get('[data-test="editParamsCancel"]').click({force: true});


    // Test Creating Mean statistic
    cy.get('[data-test="Add Statistic"]').should('be.visible')
    cy.get('[data-test="Add Statistic"]').click({force: true});
    cy.get('[data-test="Mean"]').click({force: true});
    const varDataTest = '[data-test="' + numericVar.name + '"]'
    cy.get(varDataTest).click({force: true})
    cy.get('[data-test="Fixed value"]').type(numericVar.fixedValue)
    cy.get('[data-test="Create statistic"]').click({force: true})

    // The statistic should have been created
    // cy.get('[data-test="statistic"]').should('contain', 'Mean')
    cy.get('tr').first().get('td').should('contain', 'Mean')
    cy.get('table').contains('td', 'Mean').should('be.visible');
    // Mean should contain correct accuracy value
    cy.get('table').contains('td', numericVar.accuracy).should('be.visible')


})
Cypress.Commands.add('submitMeanStatistic', () => {
    // Click Continue to go from Create Statistic to Generate DP Release Step
    cy.scrollTo('top')
    cy.get('[data-test="wizardContinueButton"]').last().click({force: true});

    // Submit Mean Statistic
    cy.get('[data-test="Submit statistics"]').click({force: true});
    // Go to Details page
    cy.get('[data-test="View Data Details"]').click({force: true});
    cy.url().should('contain', 'my-data-details')
    // The Release Details should be visible
    cy.get('[data-test="status tag"]').should('contain', 'Release Completed')
    const snippet = 'A differentially private Mean for variable'
    cy.get('[data-test="statistic description"]').should('contain', snippet)
})
Cypress.Commands.add('setupStatisticsPage', (datasetFixture, analysisFixture) => {
    cy.fixture(datasetFixture).then(dataset => {
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
        cy.fixture(analysisFixture).then(analysisPlan => {
            cy.intercept('GET', '/api/analyze/' + analysisPlan.objectId + '/', {body: analysisPlan})
        })
        cy.visit('/my-data')
        cy.get('tr').should('contain',
            'Fatigue_data.tab')
        cy.get('[data-test="continueWorkflow"]').click({force: true})
    })
})


