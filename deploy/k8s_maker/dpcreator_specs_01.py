


# dev.dpcreator.org
#
specs_01 = dict(bird='song',
                # tag used for dpcreator app and nginx
                dpcreator_app_container="ghcr.io/opendp/dpcreator/app",
                dpcreator_nginx_container="ghcr.io/opendp/dpcreator/nginx",
                dpcreator_container_tag="2021-1203", # "t01",
                #
                DEFAULT_FROM_EMAIL='info@opendp.org',
                # Make these two the same!!!
                ALLOWED_HOSTS="40.85.170.176,dev.dpcreator.org,127.0.0.1,0.0.0.0",
                loadBalancerIP="40.85.170.176",
                #
                )

# test.dpcreator.org
#
specs_01_test = dict(bird='song',
                # tag used for dpcreator app and nginx
                dpcreator_app_container="ghcr.io/opendp/dpcreator/app",
                dpcreator_nginx_container="ghcr.io/opendp/dpcreator/nginx",
                dpcreator_container_tag="2021-1203", # "t01",
                #
                DEFAULT_FROM_EMAIL='info@opendp.org',
                # Make these two the same!!!
                ALLOWED_HOSTS="13.82.125.69,test.dpcreator.org,127.0.0.1,0.0.0.0",
                loadBalancerIP="13.82.125.69",
                #
                )