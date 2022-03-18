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
Cypress.Commands.add('epsilonStep', () => {
    cy.scrollTo('top')
    cy.get('[data-test="wizardContinueButton"]').last().click({force: true});
    cy.wait('@datasetInfo', {timeout: 5000})

    cy.get('h1').should('contain', 'Set Accuracy Level').should('be.visible')
    cy.get('[data-test="Larger Population - no"]').check({force: true})
    //  cy.get('[data-test="Public Observations - yes"]').should('be.visible')
    cy.get('[data-test="Public Observations - yes"]').check({force: true})

})
Cypress.Commands.add('runDemo', (mockDVfile, demoDatafile) => {
    cy.clearData()
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

        // Submit the statistics

        cy.submitStatistics(demoData)


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
Cypress.Commands.add('selectVariable',(demoVariables)=> {
    Object.keys(demoVariables).forEach((varKey)=> {
        const demoVar = demoVariables[varKey]
        console.log('testing ' +JSON.stringify(demoVar.name))
        cy.contains('td', demoVar.name).parent('tr').should('be.visible')
        cy.contains('td', demoVar.name).parent('tr').children().first().click()
        // If numeric, enter min & max
        if (demoVar.type === 'Float' || demoVar.type === 'Integer') {
            const minDataTest = '[data-test="' + demoVar.name + ':min"]'
            const maxDataTest = '[data-test="' + demoVar.name + ':max"]'
            // Enter min and max for one numericVar so we can validate

            cy.get(minDataTest).should('be.visible')
            cy.get(maxDataTest).should('be.visible')
            cy.get(minDataTest).type(demoVar.min, {force: true})
            cy.wait(500)
            cy.get(maxDataTest).type(demoVar.max, {force: true})
            // click back into min input, to trigger change event on max input
            cy.get(minDataTest).click()
            cy.wait(500)
            cy.get(maxDataTest).should('have.value', demoVar.max)
        }
    // TODO: add handling of Categorical vars
    })

})

Cypress.Commands.add('createStatistics', (demoData) => {
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


    // Create statistic for every statistics item in the fixture
    cy.get('[data-test="Add Statistic"]').should('be.visible')
    demoData.statistics.forEach((demoStat) => {
        let demoVar = demoData.variables[demoStat.variable]
        cy.get('[data-test="Add Statistic"]').click({force: true});
        cy.get('[data-test="' + demoStat.statistic + '"]').click({force: true});
        const varDataTest = '[data-test="' + demoVar.name + '"]'
        cy.get(varDataTest).click({force: true})
        cy.get('[data-test="Fixed value"]').type(demoStat.fixedValue)
        cy.get('[data-test="Create statistic"]').click({force: true})

        // The statistic should have been created
        // cy.get('[data-test="statistic"]').should('contain', 'Mean')
        cy.get('tr').first().get('td').should('contain', demoStat.statistic)
        cy.get('table').contains('td', demoStat.statistic).should('be.visible');
        // Statistic should contain correct accuracy value
        cy.get('table').contains('td', demoStat.roundedAccuracy).should('be.visible')
    })
}),


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




})
Cypress.Commands.add('submitStatistics', (demoData) => {
    // Click Continue to go from Create Statistic to Generate DP Release Step
    cy.scrollTo('top')
    cy.get('[data-test="wizardContinueButton"]').last().click({force: true});

    // Submit  Statistic

    cy.get('h1').should('contain', 'Generate DP Release').should('be.visible')
    cy.get('[data-test="wizardSubmitStatistics"]').click({force: true});
    cy.get('[data-test="generate release status"]').should('be.visible')

    cy.get('[data-test="generate release status"]').should('contain', 'Release Completed')
    // Go to Details page
    cy.get('[data-test="View Data Details"]').click({force: true});
    cy.url().should('contain', 'my-data-details')
    // The Release Details should be visible
    cy.get('[data-test="status tag"]').should('contain', 'Release Completed')
        .then(() => {
            //    expect($p).to.contain('Release Completed')
            const sessionObj = JSON.parse(sessionStorage.getItem('vuex'))
            const releaseInfo = sessionObj.dataset.analysisPlan.releaseInfo

//dataset.analysisPlan.releaseInfo

            const testData = {
                "downloadJsonUrl": "http://localhost:8000/api/release-download/7449bc72-9858-462b-b2da-52c31ec27728/json/",
                "downloadPdfUrl": "http://localhost:8000/api/release-download/7449bc72-9858-462b-b2da-52c31ec27728/pdf/",
                "created": "2022-03-18T11:37:09.858228Z",
                "updated": "2022-03-18T11:37:17.758591Z",
                "objectId": "7449bc72-9858-462b-b2da-52c31ec27728",
                "epsilonUsed": 1,
                "dpRelease": {
                    "name": "Replication Data for: Eye-typing experiment",
                    "created": {
                        "iso": "2022-03-18T11:37:09.841967",
                        "humanReadable": "March 18, 2022 at 11:37:09:841967",
                        "humanReadableDateOnly": "5 March, 2022"
                    },
                    "dataset": {
                        "doi": "doi:10.7910/DVN/PUXVDH",
                        "name": "Replication Data for: Eye-typing experiment",
                        "type": "dataverse",
                        "citation": null,
                        "identifier": null,
                        "installation": {
                            "url": "http://127.0.0.1:8000/dv-mock-api",
                            "name": "Mock Local Dataverse"
                        },
                        "fileInformation": {
                            "name": "Fatigue_data.tab",
                            "fileFormat": "text/tab-separated-values",
                            "identifier": null
                        }
                    },
                    "statistics": [
                        {
                            "delta": null,
                            "bounds": {
                                "max": 100,
                                "min": 0
                            },
                            "result": {
                                "value": 1.226190497822561
                            },
                            "epsilon": 1,
                            "accuracy": {
                                "value": 1.6370121873967791,
                                "message": "There is a probability of 95.0% that the DP Mean will differ from the true\nMean by at most 1.6370121873967791 units. Here the units are the same units the\nvariable eyeHeight has in the dataset."
                            },
                            "variable": "eyeHeight",
                            "statistic": "mean",
                            "description": {
                                "html": "A differentially private <b>Mean</b> for variable <b>eyeHeight</b> was calculated with\nthe result <b>1.226190497822561</b>.  There is a probability of <b>95.0%</b> that the <b>DP Mean</b> will differ from\nthe true Mean by at most <b>1.6370121873967791</b> units. Here the units are the same units\nthe variable <b>eyeHeight</b> has in the dataset.\n",
                                "text": "A differentially private Mean for variable \"eyeHeight\" was calculated with the result 1.226190497822561. There is a probability of 95.0% that the DP Mean will differ from the true\nMean by at most 1.6370121873967791 units. Here the units are the same units the\nvariable eyeHeight has in the dataset."
                            },
                            "variableType": "Float",
                            "noiseMechanism": "Laplace",
                            "confidenceLevel": 0.95,
                            "confidenceLevelAlpha": 0.05,
                            "missingValueHandling": {
                                "type": "insert_fixed",
                                "fixedValue": 10
                            }
                        }
                    ],
                    "application": "DP Creator",
                    "applicationUrl": "https://github.com/opendp/dpcreator",
                    "differentiallyPrivateLibrary": {
                        "url": "https://github.com/opendp/opendp",
                        "name": "OpenDP",
                        "version": "0.3.0"
                    }
                },
                "dataverseDepositInfo": {
                    "pdfDepositRecord": {
                        "name": "ReleaseInfo object (3) - v1 (dpPDF)",
                        "created": "2022-03-18T11:37:17.750056+00:00",
                        "updated": "2022-03-18T11:37:17.750099+00:00",
                        "objectId": "7d29f0b3-1861-4ad6-9ca1-f178cb3e09d5",
                        "dvErrMsg": "The deposit failed. Dataverse returned a \"Forbidden\" error. (Dataverse url: http://127.0.0.1:8000/dv-mock-api).",
                        "dvUploadUrl": "http://127.0.0.1:8000/dv-mock-api/api/access/datafile/4164587/auxiliary/dpPDF/v1",
                        "userMsgHtml": "Error. The dpPDF release file was not deposited to Dataverse.\n(Dataverse message: The deposit failed. Dataverse returned a &quot;Forbidden&quot; error. (Dataverse url: http://127.0.0.1:8000/dv-mock-api).)\n\n\n",
                        "userMsgText": "Error. The dpPDF release file was not deposited to Dataverse.\n(Dataverse message: The deposit failed. Dataverse returned a &quot;Forbidden&quot; error. (Dataverse url: http://127.0.0.1:8000/dv-mock-api).)\n\n",
                        "httpRespJson": null,
                        "httpRespText": "\n<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n  <meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\">\n  <meta name=\"robots\" content=\"NONE,NOARCHIVE\">\n  <title>403 Forbidden</title>\n  <style type=\"text/css\">\n    html * { padding:0; margin:0; }\n    body * { padding:10px 20px; }\n    body * * { padding:0; }\n    body { font:small sans-serif; background:#eee; color:#000; }\n    body>div { border-bottom:1px solid #ddd; }\n    h1 { font-weight:normal; margin-bottom:.4em; }\n    h1 span { font-size:60%; color:#666; font-weight:normal; }\n    #info { background:#f6f6f6; }\n    #info ul { margin: 0.5em 4em; }\n    #info p, #summary p { padding-top:10px; }\n    #summary { background: #ffc; }\n    #explanation { background:#eee; border-bottom: 0px none; }\n  </style>\n</head>\n<body>\n<div id=\"summary\">\n  <h1>Forbidden <span>(403)</span></h1>\n  <p>CSRF verification failed. Request aborted.</p>\n\n\n  <p>You are seeing this message because this site requires a CSRF cookie when submitting forms. This cookie is required for security reasons, to ensure that your browser is not being hijacked by third parties.</p>\n  <p>If you have configured your browser to disable cookies, please re-enable them, at least for this site, or for âsame-originâ requests.</p>\n\n</div>\n\n<div id=\"info\">\n  <h2>Help</h2>\n    \n    <p>Reason given for failure:</p>\n    <pre>\n    CSRF cookie not set.\n    </pre>\n    \n\n  <p>In general, this can occur when there is a genuine Cross Site Request Forgery, or when\n  <a\n  href=\"https://docs.djangoproject.com/en/3.1/ref/csrf/\">Django's\n  CSRF mechanism</a> has not been used correctly.  For POST forms, you need to\n  ensure:</p>\n\n  <ul>\n    <li>Your browser is accepting cookies.</li>\n\n    <li>The view function passes a <code>request</code> to the template's <a\n    href=\"https://docs.djangoproject.com/en/dev/topics/templates/#django.template.backends.base.Template.render\"><code>render</code></a>\n    method.</li>\n\n    <li>In the template, there is a <code>{% csrf_token\n    %}</code> template tag inside each POST form that\n    targets an internal URL.</li>\n\n    <li>If you are not using <code>CsrfViewMiddleware</code>, then you must use\n    <code>csrf_protect</code> on any views that use the <code>csrf_token</code>\n    template tag, as well as those that accept the POST data.</li>\n\n    <li>The form has a valid CSRF token. After logging in in another browser\n    tab or hitting the back button after a login, you may need to reload the\n    page with the form, because the token is rotated after a login.</li>\n  </ul>\n\n  <p>You're seeing the help section of this page because you have <code>DEBUG =\n  True</code> in your Django settings file. Change that to <code>False</code>,\n  and only the initial error message will be displayed.  </p>\n\n  <p>You can customize this page using the CSRF_FAILURE_VIEW setting.</p>\n</div>\n\n</body>\n</html>\n",
                        "depositSuccess": false,
                        "dvDownloadUrl": null,
                        "httpStatusCode": 403,
                        "dvAuxiliaryType": "dpPDF",
                        "dvAuxiliaryVersion": "v1"
                    },
                    "jsonDepositRecord": {
                        "name": "ReleaseInfo object (3) - v1 (dpJson)",
                        "created": "2022-03-18T11:37:17.696130+00:00",
                        "updated": "2022-03-18T11:37:17.696170+00:00",
                        "objectId": "3844017a-d6a5-4fbd-a776-07f7566b7a82",
                        "dvErrMsg": "The deposit failed. Dataverse returned a \"Forbidden\" error. (Dataverse url: http://127.0.0.1:8000/dv-mock-api).",
                        "dvUploadUrl": "http://127.0.0.1:8000/dv-mock-api/api/access/datafile/4164587/auxiliary/dpJson/v1",
                        "userMsgHtml": "Error. The dpJson release file was not deposited to Dataverse.\n(Dataverse message: The deposit failed. Dataverse returned a &quot;Forbidden&quot; error. (Dataverse url: http://127.0.0.1:8000/dv-mock-api).)\n\n\n",
                        "userMsgText": "Error. The dpJson release file was not deposited to Dataverse.\n(Dataverse message: The deposit failed. Dataverse returned a &quot;Forbidden&quot; error. (Dataverse url: http://127.0.0.1:8000/dv-mock-api).)\n\n",
                        "httpRespJson": null,
                        "httpRespText": "\n<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n  <meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\">\n  <meta name=\"robots\" content=\"NONE,NOARCHIVE\">\n  <title>403 Forbidden</title>\n  <style type=\"text/css\">\n    html * { padding:0; margin:0; }\n    body * { padding:10px 20px; }\n    body * * { padding:0; }\n    body { font:small sans-serif; background:#eee; color:#000; }\n    body>div { border-bottom:1px solid #ddd; }\n    h1 { font-weight:normal; margin-bottom:.4em; }\n    h1 span { font-size:60%; color:#666; font-weight:normal; }\n    #info { background:#f6f6f6; }\n    #info ul { margin: 0.5em 4em; }\n    #info p, #summary p { padding-top:10px; }\n    #summary { background: #ffc; }\n    #explanation { background:#eee; border-bottom: 0px none; }\n  </style>\n</head>\n<body>\n<div id=\"summary\">\n  <h1>Forbidden <span>(403)</span></h1>\n  <p>CSRF verification failed. Request aborted.</p>\n\n\n  <p>You are seeing this message because this site requires a CSRF cookie when submitting forms. This cookie is required for security reasons, to ensure that your browser is not being hijacked by third parties.</p>\n  <p>If you have configured your browser to disable cookies, please re-enable them, at least for this site, or for âsame-originâ requests.</p>\n\n</div>\n\n<div id=\"info\">\n  <h2>Help</h2>\n    \n    <p>Reason given for failure:</p>\n    <pre>\n    CSRF cookie not set.\n    </pre>\n    \n\n  <p>In general, this can occur when there is a genuine Cross Site Request Forgery, or when\n  <a\n  href=\"https://docs.djangoproject.com/en/3.1/ref/csrf/\">Django's\n  CSRF mechanism</a> has not been used correctly.  For POST forms, you need to\n  ensure:</p>\n\n  <ul>\n    <li>Your browser is accepting cookies.</li>\n\n    <li>The view function passes a <code>request</code> to the template's <a\n    href=\"https://docs.djangoproject.com/en/dev/topics/templates/#django.template.backends.base.Template.render\"><code>render</code></a>\n    method.</li>\n\n    <li>In the template, there is a <code>{% csrf_token\n    %}</code> template tag inside each POST form that\n    targets an internal URL.</li>\n\n    <li>If you are not using <code>CsrfViewMiddleware</code>, then you must use\n    <code>csrf_protect</code> on any views that use the <code>csrf_token</code>\n    template tag, as well as those that accept the POST data.</li>\n\n    <li>The form has a valid CSRF token. After logging in in another browser\n    tab or hitting the back button after a login, you may need to reload the\n    page with the form, because the token is rotated after a login.</li>\n  </ul>\n\n  <p>You're seeing the help section of this page because you have <code>DEBUG =\n  True</code> in your Django settings file. Change that to <code>False</code>,\n  and only the initial error message will be displayed.  </p>\n\n  <p>You can customize this page using the CSRF_FAILURE_VIEW setting.</p>\n</div>\n\n</body>\n</html>\n",
                        "depositSuccess": false,
                        "dvDownloadUrl": null,
                        "httpStatusCode": 403,
                        "dvAuxiliaryType": "dpJson",
                        "dvAuxiliaryVersion": "v1"
                    }
                },
                "dvJsonDepositComplete": false,
                "dvPdfDepositComplete": false
            }

            demoData.statistics.forEach((demoStat) => {
                expect(releaseInfo.dpRelease.statistics[0].statistic).to.equal(demoStat.statistic.toLowerCase())
                expect(releaseInfo.dpRelease.statistics[0].accuracy.value).to.equal(demoStat.accuracy)
                //  cy.get('[data-test="statistic description"]').should('contain', demoStat.statistic)
                //   cy.get('[data-test="statistic description"]').should('contain', demoStat.accuracy)
            })
        })
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
            'Replication Data for: Eye-typing experiment')
        cy.get('[data-test="continueWorkflow"]').click({force: true})
    })
})


