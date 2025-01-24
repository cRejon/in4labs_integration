from tempfile import mkdtemp
import os


basedir = os.path.abspath(os.path.dirname(__file__))
nodered_dir = os.path.join(basedir, os.pardir, 'node-red')
nodered_settings_file = os.path.join(nodered_dir, 'settings.js')

class Config(object):
    # Labs settings
    labs_config = {
        'duration': 15, # minutes
        'labs': [{
            'lab_name' : 'in4labs_integration',
            'html_name' : 'Integration System Laboratory',
            'description' : 'In4Labs laboratory for integration systems.',
            'host_port' : 8001,
            'volumes': {'integration_lab_vol': {'bind': '/app/node-red/data', 'mode': 'ro'}},
            'cam_url': 'http://ULR_TO_WEBCAM/Mjpeg',
            'extra_containers': [{
                'name': 'node-red',
                'image': 'in4labs_nodered:latest',
                'nat_port': 1880,
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