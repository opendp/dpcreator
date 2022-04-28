"""
Environment variables used in the k8s deployment files
"""

base_specs = dict(
                deploy_name="!add-deploy-name!",
                #
                dpcreator_app_container="ghcr.io/opendp/dpcreator/app",     # app image (server + compiled Vue.js)
                dpcreator_nginx_container="ghcr.io/opendp/dpcreator/nginx",  # Nginx image
                dpcreator_container_tag="latest",  # Tag for Images
                #
                DEFAULT_FROM_EMAIL='info@opendp.org',  # Related to the Sendgrid API call
                #
                ACCOUNT_EMAIL_VERIFICATION="mandatory",  # Django allauth. See server/opendp_apps/user/README.md
                #
                # relates to info@opendp.org account
                VUE_APP_GOOGLE_CLIENT_ID="750757442540-4bg3aulcrm802i8pguo851lq8kikf5ge.apps.googleusercontent.com",
                VUE_APP_ADOBE_PDF_CLIENT_ID="(Needs to be set!)",
                #
                # DEPLOYMENT SPECIFIC VARIABLES:
                dpcreator_startup_script_filename="Needs to be set! (See: base_specs)",
                ALLOWED_HOSTS="Needs to be set! (See: base_specs)",  # Django setting
                #
                # This loadBalancerIP should also appear in ALLOWED_HOSTS
                loadBalancerIP="Needs to be set! (See: base_specs)",  # k8s LoadBalancer.
                )

# dev.dpcreator.org
#
specs_dev_dpcreator_org = dict(base_specs, **dict(
                # DEPLOYMENT SPECIFIC VARIABLES:
                deploy_name="dev",
                #
                dpcreator_startup_script_filename="azure_dev.dpcreator.org.sh",
                #
                ALLOWED_HOSTS="40.85.170.176,dev.dpcreator.org,127.0.0.1,0.0.0.0",  # Django setting
                # This loadBalancerIP should also appear in ALLOWED_HOSTS
                loadBalancerIP="40.85.170.176",  # k8s LoadBalancer.
                #
                SECURE_SSL_REDIRECT="True",
                USE_SSL_PROXY="False",
                #
                VUE_APP_ADOBE_PDF_CLIENT_ID="34a0c926740d4ddb9758dbc6da2a4f39",
                VUE_APP_WEBSOCKET_PREFIX='wss://',
                ))

# demo.dpcreator.org
#
specs_demo_dpcreator_org = dict(base_specs, **dict(
                # DEPLOYMENT SPECIFIC VARIABLES:
                deploy_name="demo",
                #
                dpcreator_startup_script_filename="azure_demo.dpcreator.org.sh",
                #
                # dpcreator_container_tag="dpcreator-demo",  # Tag for Images
                #
                ALLOWED_HOSTS="13.82.125.69,demo.dpcreator.org,127.0.0.1,0.0.0.0",  # Django setting
                # This loadBalancerIP should also appear in ALLOWED_HOSTS
                loadBalancerIP="13.82.125.69",   # k8s LoadBalancer.
                #
                SECURE_SSL_REDIRECT="True",
                USE_SSL_PROXY="False",
                #
                VUE_APP_ADOBE_PDF_CLIENT_ID="44937032e26b4033a840626ed0cd8e79",
                VUE_APP_WEBSOCKET_PREFIX='wss://',
))
