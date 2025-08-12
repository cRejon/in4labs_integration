import os


class Config(object):
    # Boards configuration
    boards_config = {
        'Board_1':{
            'name':'Sensor',
            'model':'Arduino Nano ESP32', 
            'fqbn':'arduino:esp32:nano_nora', 
            'usb_port':'1',
        },
        'Board_2':{
            'name':'LCD',
            'model':'Arduino Nano ESP32',
            'fqbn':'arduino:esp32:nano_nora',
            'usb_port':'2',
        },
        'Board_3':{
            'name':'Fan',
            'model':'Arduino Nano ESP32',
            'fqbn':'arduino:esp32:nano_nora',
            'usb_port':'3',
        }
    }

    # Docker environment variables
    server_name = os.environ.get('SERVER_NAME')
    lab_name = os.environ.get('LAB_NAME')
    user_email = os.environ.get('USER_EMAIL') 
    end_time = os.environ.get('END_TIME') 
    cam_url = os.environ.get('CAM_URL') 

    # Flask environment variable needed for session management
    flask_config = {
        # Use as secret key the user email + the end time of the session 
        'SECRET_KEY': user_email + end_time,
        'SESSION_COOKIE_NAME': user_email + end_time,
    }
