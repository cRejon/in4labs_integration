from tempfile import mkdtemp


class Config(object):
    
    # Flask settings
    ENV = 'development'
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 600
    SECRET_KEY = 'replace-me', # change in production
    SESSION_TYPE= 'filesystem',
    SESSION_FILE_DIR = mkdtemp(),
    SESSION_COOKIE_NAME = 'app-sessionid' 
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False   # should be True in case of HTTPS usage (production)
    SESSION_COOKIE_SAMESITE = None  # should be 'None' in case of HTTPS usage (production)
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # Labs settings
    labs_config = {
        'duration': 15, # minutes
        'labs': [{
            'lab_name' : 'in4labs_integration',
            'html_name' : 'Integration System Laboratory',
            'description' : 'In4Labs laboratory for integration systems.',
            'host_port' : 8001,
            'cam_url': 'http://ULR_TO_WEBCAM/Mjpeg',
            'extra_containers': [{
                'name': 'node-red',
                'image': 'nodered/node-red',
                'nat_port': 1880,
                'ports': {'1880/tcp': ('0.0.0.0', 1880)},
                'network': 'integration_lab_net',
                }, {
                'name': 'mosquitto',
                'image': 'eclipse-mosquitto',
                'ports': {'1883/tcp': ('192.168.4.0', 1883)},
                'network': 'integration_lab_net',
                'command': 'mosquitto -c /mosquitto-no-auth.conf',
                },
            ],
        }],
    }