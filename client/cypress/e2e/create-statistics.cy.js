{
    describe('Create Statistics Wizard Step tests', () => {
        before(() => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })

        })
        beforeEach(() => {
            cy.loadTeacherSurveyDemo()
        })
        afterEach(() => {
            cy.logout()
        })
        //TODO: uncomment when analysis is ready
/*
        it('Goes back to the Confirm Variables Page', () => {
            const meanAge = {
                "statistics": [
                    {
                        "statistic": "Mean",
                        "variable": "age",
                        "fixedValue": "35",
                        "roundedAccuracy": "0.0235",
                    }
                ]

            }

            cy.enterStatsInPopup(meanAge)
            cy.get('[data-test="Add Statistic"]').should('be.visible')
            cy.get('[data-test="Add Statistic"]').click({force: true});
            cy.get('[data-test="confirmVariablesLink"]').click({force: true});
            cy.get('h1').should('contain', 'Confirm Variables').should('be.visible')
            // The checkbox for variable that was used to create a statistic should be disabled
            // on the confirm variables page
            cy.contains('td', meanAge.statistics[0].variable).parent('tr').children()
                .first().children().get(":has(.v-simple-checkbox--disabled)").should('be.visible')
        })

        afterEach(() => {
            cy.logout()
        })

        it('Validates fixed value max-min', () => {
            const varMax = 75
            const varMin = 20
            const testMax = Number(varMax + 1)
            const testMin = Number(varMin - 1)
            const varName = "age"
            cy.get('[data-test="Add Statistic"]').click({force: true});
            cy.get('[data-test="AddStatisticDialog"]').should('be.visible')

            cy.get('[data-test="Mean"]').click({force: true});
            const varDataTest = '[data-test="' + varName + '"]'
            cy.get(varDataTest).click({force: true})
            cy.get('[data-test="Fixed value"]').type(testMax)
            cy.get('div').should('contain', 'Value must be between')
            cy.get('[data-test="Fixed value"]').clear()
            cy.get('[data-test="Fixed value"]').type(testMin)
            cy.get('div').should('contain', 'Value must be between')
            cy.get('[data-test="Fixed value"]').clear()
            cy.get('[data-test="Fixed value"]').type(varMax)
            cy.get('div').should('not.contain', 'Value must be between')

        })
        it('Goes to the correct wizard step', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.get('h1').should('contain', 'Create Statistics')
        })
        it('Populates Edit Noise Param Dialog', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.get('h1').should('contain', 'Create Statistics')
            cy.get('[data-test="editConfidenceIcon"]').click({force: true});
            cy.get('h2').should('contain', 'Are you sure you want to proceed?').should('be.visible')
            cy.get('[data-test="confirmButton"]').click({force: true});

            cy.get('[data-test="editEpsilonInput"]').should('have.value', 1)
            cy.get('[data-test="editParamsCancel"]').click({force: true});

        })
        it('Contains correct variables in the Add Statistics dialog ', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.fixture('TeacherSurveyVariableInfo').then((analysisFixture) => {
                // Create your statistic
                cy.get('[data-test="Add Statistic"]').click({force: true});
                for (const key in analysisFixture.variableInfo) {
                    if (analysisFixture.variableInfo[key].selected) {
                        cy.get('label').should('contain', analysisFixture.variableInfo[key].name)
                    } else {
                        cy.get('label').should('not.contain', analysisFixture.variableInfo[key].name)
                    }
                }
                cy.get('[data-test="Mean"]').click({force: true});
                for (const key in analysisFixture.variableInfo) {
                    if (!analysisFixture.variableInfo[key].selected ||
                        (analysisFixture.variableInfo[key].type !== 'Integer' &&
                            analysisFixture.variableInfo[key].type !== 'Float')) {
                        cy.get('label').should('not.contain', analysisFixture.variableInfo[key].name)
                    }
                }
                cy.get('[data-test="Add Statistic Close"]').click({force: true})
            })

        })
*/

    })
}