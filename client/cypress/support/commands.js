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
    cy.login('dev_admin', 'admin')
    cy.request('/cypress-tests/clear-test-data/')


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
            if (demoData.variables[key].type == "Numerical") {
                numericVar = demoData.variables[key]
            }
        }
        if (numericVar !== null) {
            cy.testMean(numericVar)
        }

    })

})


Cypress.Commands.add('createMockDataset', (fixture) => {
    cy.fixture(fixture).then((mockForm) => {
        cy.visit('/mock-dv');
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
        // first we will be routed to the Terms of Conditions page for the user
        cy.get('[data-test="confirmTermsCheckbox"]').click({force: true});
        cy.get('[data-test="confirmTermsContinue"]').click();
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
    cy.get('[data-test="wizardContinueButton"]').last().click();
    cy.wait('@datasetInfo')
    cy.get('h1').should('contain', 'Confirm Variables')
    for (const key in variableData) {
        const val = variableData[key]
        cy.get('table').contains('td', val.name).should('be.visible')
        cy.get('table').contains('tr', val.name).should('contain', val.type)
    }


})

Cypress.Commands.add('testMean', (numericVar) => {
    cy.intercept('PATCH', '/api/deposit/**',).as(
        'patchDeposit'
    )
    cy.intercept('GET', '/api/dataset-info/**',).as(
        'datasetInfo'
    )
    const minDataTest = '[data-test="' + numericVar.name + ':min"]'
    const maxDataTest = '[data-test="' + numericVar.name + ':max"]'
    // Enter min and max for one numericVar so we can validate
    cy.get(minDataTest).should('be.visible')
    cy.get(maxDataTest).should('be.visible')
    cy.get(minDataTest).type(numericVar.min, {force: true})
    cy.wait(500)
    cy.get(maxDataTest).type(numericVar.max, {force: true})
    cy.wait('@patchDeposit', {timeout: 5000})

    // Continue to Set Epsilon Step
    cy.get('[data-test="wizardContinueButton"]').last().click();
    cy.wait('@datasetInfo', {timeout: 5000})

    cy.get('h1').should('contain', 'Set epsilon value').should('be.visible')
    cy.get('[data-test="Larger Population - no"]').check({force: true})
    //  cy.get('[data-test="Public Observations - yes"]').should('be.visible')
    cy.get('[data-test="Public Observations - yes"]').check({force: true})


    // Continue to Create  Statistics Step
    cy.get('[data-test="wizardContinueButton"]').last().click();
    cy.wait('@datasetInfo', {timeout: 5000})

    // On the statistics page,
    cy.get('h1').should('contain', 'Create the statistics').should('be.visible')


    // Test Validating EyeHeight mean
    cy.get('[data-test="Add Statistic"]').should('be.visible')
    cy.get('[data-test="Add Statistic"]').click({force: true});
    cy.get('[data-test="Mean"]').click({force: true});
    const varDataTest = '[data-test="' + numericVar.name + '"]'
    cy.get(varDataTest).click({force: true})
    cy.get('[data-test="Insert fixed value"]').click({force: true})
    cy.get('[data-test="Fixed value"]').type(numericVar.fixedValue)
    cy.get('[data-test="Create statistic"]').click({force: true})

    // The statistic should have been created
    // cy.get('[data-test="statistic"]').should('contain', 'Mean')
    cy.get('tr').first().get('td').should('contain', 'Mean')
    cy.get('table').contains('td', 'Mean').should('be.visible');
    // Mean should contain correct accuracy value
    cy.get('table').contains('td', numericVar.accuracy).should('be.visible')
    // Click Continue to go to Generate DP Release Step
    cy.get('[data-test="wizardContinueButton"]').last().click();

    // Submit Statistic
    cy.get('[data-test="Submit statistics"]').click({force: true});

    // Go to Details page
    cy.get('[data-test="View Data Details"]').click({force: true});
    cy.url().should('contain', 'my-data-details')
    // The Release Details should be visible
    cy.get('[data-test="status tag"]').should('contain', 'Release completed')
    cy.get('[data-test="DP Statistics Panel"]').click({force: true})
    cy.get('[data-test="DP Statistics Panel"]').should('contain', 'statistic:"mean"')
    // The statistic description should be visible
    cy.get('[data-test="DP Statistics Panel"]').should('contain', 'statistic:"mean"')
    const snippet = 'A differentially private'
    cy.get('[data-test="statistic description"]').should('contain', snippet)

})
