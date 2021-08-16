


specs_01 = dict(bird='song',
                # tag used for dpcreator app and nginx
                dpcreator_app_container="ghcr.io/opendp/dpcreator/app",
                dpcreator_nginx_container="ghcr.io/opendp/dpcreator/nginx",
                dpcreator_container_tag="2021-0712", # "t01",
                #
                DEFAULT_FROM_EMAIL='smartnoise@opendp.org',
                # Make these two the same!!!
                ALLOWED_HOSTS="13.92.177.209,dev.dpcreator.org,127.0.0.1,0.0.0.0",
                loadBalancerIP="13.92.177.209",
                #
                )
