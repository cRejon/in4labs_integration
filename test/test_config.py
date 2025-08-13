import os


basedir = os.path.abspath(os.path.dirname(__file__))
nodered_dir = os.path.join(basedir, os.pardir, 'node-red')
nodered_settings_file = os.path.join(nodered_dir, 'settings.js')

class Config(object):
    # Labs settings
    labs_config = {
        'server_name': 'test_server',
        'mountings': [{
            'id': '1', 
            'duration': 10, # minutes
            'cam_url': 'https://ULR_TO_WEBCAM/stream.m3u8',
            'host_port' : 8001,
        },],
        'labs': [{
            'lab_name' : 'in4labs_integration',
            'html_name' : 'Integration System Laboratory',
            'description' : 'In4Labs laboratory for integration systems.',
            'mounting_id': '1',
            'volumes': {'integration_lab_vol': {'bind': '/app/node-red/data', 'mode': 'ro'}},
            'extra_containers': [{
                'name': 'node-red',
                'image': 'in4labs_nodered:latest',
                'ports': {'1880/tcp': ('0.0.0.0', 1880)},
                'volumes': {'integration_lab_vol': {'bind': '/data', 'mode': 'rw'},
                            nodered_settings_file: {'bind': '/data/settings.js', 'mode': 'ro'}},
                'network': 'integration_lab_net',
                }, {
                'name': 'mosquitto',
                'image': 'eclipse-mosquitto:latest',
                'ports': {'1883/tcp': ('192.168.4.1', 1883)},
                'network': 'integration_lab_net',
                'command': 'mosquitto -c /mosquitto-no-auth.conf',
                },
            ],
        }],
    }