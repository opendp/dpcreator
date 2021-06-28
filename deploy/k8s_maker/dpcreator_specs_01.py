


specs_01 = dict(bird='song',
                # tag used for dpcreator app and nginx
                dpcreator_app_container="ghcr.io/opendp/dpcreator/app",
                dpcreator_nginx_container="ghcr.io/opendp/dpcreator/nginx",
                dpcreator_container_tag="2021-0624", # "t01",
                #
                DEFAULT_FROM_EMAIL='smartnoise@opendp.org',
                # Make these two the same!!!
                ALLOWED_HOSTS="52.147.198.81,dev.dpcreator.org,127.0.0.1,0.0.0.0",
                loadBalancerIP="52.147.198.81",
                #
                )
