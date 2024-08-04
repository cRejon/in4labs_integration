import os
import subprocess
import time

import pexpect
import requests
from flask import Flask, render_template, url_for, jsonify, redirect, send_file, flash, request
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user

from .utils import get_serial_number, get_usb_driver, create_editor, create_navtab


# Flask environment variable needed for session management
flask_config = {
    # Use as secret key the user email + the end time of the session 
    'SECRET_KEY': os.environ.get('USER_EMAIL') + os.environ.get('END_TIME'),
}

# Docker environment variables
cam_url = os.environ.get('CAM_URL') 
user_email = os.environ.get('USER_EMAIL') 
end_time = os.environ.get('END_TIME') 
node_red_url = os.environ.get('NODE_RED_URL')

# Boards configuration
boards = {
    'Board_1':{
        'name':'LCD',
        'role':'Master',
        #'model':'Arduino Uno WiFi Rev2',
        #'fqbn':'arduino:megaavr:uno2018',
        'model':'Arduino Nano ESP32',
        'fqbn':'arduino:esp32:nano_nora',
        'usb_port':'2',
    },
    'Board_2':{
        'name':'Sensor',
        'role':'Slave',
        'model':'Arduino Nano ESP32',
        'fqbn':'arduino:esp32:nano_nora',
        'usb_port':'1',
    },
    'Board_3':{
        'name':'Fan',
        'role':'Slave',
        'model':'Arduino Nano ESP32',
        'fqbn':'arduino:esp32:nano_nora',
        'usb_port':'3',
    }
}

boards = get_serial_number(boards) # Get the serial number of the boards

app = Flask(__name__)
app.config.from_mapping(flask_config)
app_dir = os.path.abspath('/app')
arduino_dir = os.path.join(app_dir, 'arduino')
nodered_dir = os.path.join(app_dir, 'node-red')

# Create the subfolders for the compilations
try:
    for board in boards.keys():
        os.makedirs(os.path.join(arduino_dir, 'compilations', board))
        for dir in ['build', 'cache', 'temp_sketch']:
            os.makedirs(os.path.join(arduino_dir, 'compilations', board, dir))
except OSError:
    pass

# Flask-Login configuration
login_manager = LoginManager()
login_manager.login_view = 'login' # Set the default login page
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return user

class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

user = User(id=1, email=user_email)


# Flask routes
@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index')) 

    if request.method == 'POST':
        email = request.form['email']
        if email == user_email:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid email address. Please try again.')
    
    return render_template('login.html')

@app.route('/index')
@login_required
def index():
    navtabs = []
    editors = []
    for board in boards.items():
        navtabs.append(create_navtab(board))
        editors.append(create_editor(board))
    return render_template('index.html', boards=boards, navtabs=navtabs, node_red_url=node_red_url,
                                editors=editors, cam_url=cam_url, end_time=end_time)

@app.route('/get_example', methods=['GET'])
@login_required
def get_example(): 
    example = request.args.get('example')      
    examples_path = os.path.join(arduino_dir, 'examples')

    # Find example file in the corresponding folder
    for folder in os.listdir(examples_path):
        if example in os.listdir(os.path.join(examples_path, folder)):
            example_file = os.path.join(examples_path, folder, example)
            break

    return send_file(example_file, mimetype='text')

@app.route('/compile', methods=['POST'])
@login_required
def compile():
    board = request.form['board']
    code = request.form['text']

    compilation_path = os.path.join(arduino_dir, 'compilations', board)
    sketch_path = os.path.join(compilation_path, 'temp_sketch')

    with open(os.path.join(sketch_path, 'temp_sketch.ino'), 'w') as f:
        f.write(code)

    command = ['arduino-cli', 'compile', '--fqbn', boards[board]['fqbn'],
    '--build-cache-path', os.path.join(compilation_path, 'cache'), 
    '--build-path', os.path.join(compilation_path, 'build'), 
    sketch_path]

    result = subprocess.run(command, capture_output=True, text=True) 

    resp = jsonify(board=board, error=result.stderr)
    return resp

@app.route('/execute', methods=['POST'])
@login_required
def execute():
    board = request.form['board']
    target = request.form['target']

    load_sketch(board, target)

    resp = jsonify(board=board)
    return resp

def load_sketch(board, target):
    if boards[board]['model'] == 'Arduino Nano ESP32':
        if (target == 'user'): 
            input_file = os.path.join(arduino_dir, 'compilations', board, 'build', 'temp_sketch.ino.bin')
        else: # target == 'stop'
            input_file = os.path.join(arduino_dir, 'compilations', 'precompiled','stop.ino.bin')

        dfu_util = os.path.join('/', 'root', '.arduino15', 'packages', 'arduino',
                                    'tools', 'dfu-util', '0.11.0-arduino5', 'dfu-util')
        serial_number = boards[board]['serial_number']

        command = [dfu_util, '--serial', serial_number, '-D', input_file, '-Q']

    elif boards[board]['model'] == 'Arduino Uno WiFi Rev2':
        # NOTE: Arduino-cli uses AVRdude to upload the code and it does not work properly if -Pusb flag is used with 
        #       the usb interface of the board, so we use the last two digits of the serial number instead.
        if (target == 'user'): 
            input_file = os.path.join(arduino_dir, 'compilations', board, 'build', 'temp_sketch.ino.hex')
        else: # target == 'stop'
            input_file = os.path.join(arduino_dir, 'compilations', 'precompiled','stop.ino.hex')

        serial_number = boards[board]['serial_number'][-2:]
        avrdude_path = os.path.join('/', 'root', '.arduino15', 'packages', 'arduino',
                                    'tools', 'avrdude', '6.3.0-arduino17', 'bin', 'avrdude')
        avrdude_conf_path = os.path.join('/', 'root', '.arduino15', 'packages', 'arduino', 
                                        'tools', 'avrdude', '6.3.0-arduino17', 'etc', 'avrdude.conf')
        avrdude_partno = 'atmega4809'
        avrdude_programer_id = 'xplainedmini_updi'
        avrdude_usb_port = '-Pusb:'+ serial_number
        avrdude_baudrate = '115200'
        avrdude_sketch =  '-Uflash:w:'+ input_file +':i'
        avrdude_fuse_2 = '-Ufuse2:w:0x01:m'
        avrdude_fuse_5 = '-Ufuse5:w:0xC9:m'
        avrdude_fuse_8 = '-Ufuse8:w:0x02:m'
        avrdude_boot = os.path.join('/', 'root', '.arduino15', 'packages', 'arduino',
                                    'hardware', 'megaavr', '1.8.8', 'bootloaders', 'atmega4809_uart_bl.hex:i')

        command = [avrdude_path, '-C', avrdude_conf_path, '-V', '-p', avrdude_partno, '-c', avrdude_programer_id, 
                avrdude_usb_port, '-b', avrdude_baudrate, '-e', '-D', avrdude_sketch, avrdude_fuse_2, 
                avrdude_fuse_5, avrdude_fuse_8, avrdude_boot]

    result = subprocess.run(command, capture_output=True, text=True) 
    print(result) # Debug info

@app.route('/monitor', methods=['GET'])
@login_required
def monitor():
    global boards
    boards = get_usb_driver(boards) # Get the drivers of the boards
    
    board = request.args.get('board')
    baudrate = request.args.get('baudrate', default=9600, type=int)
    seconds = request.args.get('seconds', default=10, type=int)

    usb_driver = boards[board]['usb_driver']

    command = f'arduino-cli monitor -p /dev/{usb_driver} --quiet --config baudrate={baudrate}'
    # NOTE: pexpect is used because arduino-cli monitor expects to run in an interactive 
    #       terminal environment and subprocess.run() does not work properly.
    child = pexpect.spawn(command)
    
    try:
        child.expect(pexpect.EOF, timeout=seconds)
    except pexpect.TIMEOUT:
        pass

    output = child.before.decode('utf-8')
    
    child.close()
        
    resp = jsonify(board=board, output=output)
    return resp

@app.route('/suggest', methods=['POST'])
@login_required
def suggest():
    board = request.form['board']
    code = request.form['text']

    data = {'action': '16', 'text': code}
    url = 'https://open.ieec.uned.es/v_innovacion/api.php'

    r = requests.post(url, data=data)
    suggestion = r.text

    resp = jsonify(board=board, suggestion=suggestion)
    return resp

@app.route('/reset_lab', methods=['GET'])
@login_required
def reset():
    # Uhubctl is used to power on/off the USB ports of the Raspberry Pi
    command = ['uhubctl', '-a', 'cycle', '-l', '1-1', '-d', '2']
    result = subprocess.run(command, capture_output=True, text=True)
    # Load the stop code in all the boards
    time.sleep(1)
    for board in boards:
        print('Loading stop code in ' + board)
        load_sketch(board, 'stop')
    # Return the output of the command for debugging purposes
    resp = jsonify(result=result.stdout)
    return resp

@app.route('/get_flows', methods=['GET'])
@login_required
def get_flows(): 
    nodered_data_dir = os.path.join(nodered_dir, 'data')
    flows_file = os.path.join(nodered_data_dir, 'flows.json')
    with open(flows_file, 'r') as f:
        flows = f.read()
    return jsonify(flows=flows)

