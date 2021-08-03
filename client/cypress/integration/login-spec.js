{
    describe('Login', () => {
        const getStore = () => cy.window().its('app.$store')
        it('successfully updates vuex store', () => {
            cy.visit('/')
            getStore().its('state.auth.user').should('deep.equal', null)
            cy.login('dev_admin', 'admin')
            getStore().its('state.auth.user.username').should('deep.equal', 'dev_admin')
            cy.request('/api/users/1/').then((data) => {
                console.log(data.body.object_id)
            })


        })
    })
}