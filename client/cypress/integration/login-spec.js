{
    describe('Login', () => {
        const getStore = () => cy.window().its('app.$store')
        it('uses login API', () => {
            cy.loginAPI('dev_admin', 'admin')
        })
        it('successfully updates vuex store', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.visit('/')
            getStore().its('state.auth.user').should('deep.equal', null)
            cy.login('dev_admin', 'admin')
            getStore().its('state.auth.user.username').should('deep.equal', 'dev_admin')
            cy.request('/api/users/1/').then((data) => {
                console.log(data.body.object_id)
            })


        })
        it('submits form on enter', () => {
            cy.clearData()
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            let user = "cookie"
            let email = "cookie@monster.com"
            let password = "cookie123!"
            cy.createAccount(user, email, password)
            cy.logout()
            cy.visit('/log-in')
            cy.get('[data-test="username"]').type(user);
            cy.get('[data-test="password"]').type(password);
            cy.get('[data-test="password"]').type("{enter}")
            cy.url().should('contain', 'my-data')

        })

    })
}