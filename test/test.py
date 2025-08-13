import os
import re
import subprocess
import threading
import time
from datetime import datetime, timedelta, timezone
import atexit

import bcrypt
import docker

from test_config import Config


basedir = os.path.abspath(os.path.dirname(__file__))

# Class to stop the containers when the time is up
class StopContainersTask(threading.Thread):
     def __init__(self, containers, end_time):
         super(StopContainersTask, self).__init__()
         self.containers = containers
         self.end_time = end_time
 
     def run(self):
        remaining_secs = (end_time - datetime.now(timezone.utc)).total_seconds()
        time.sleep(remaining_secs)
        for container in self.containers:
            container.stop()
        print('Lab containers stopped.')

# Function to create a Docker image from a Dockerfile
def create_docker_image(image_name, dockerfile_path):
    print(f'Creating Docker image {image_name}. Be patient, this will take a while...')
    image, build_logs = client.images.build(
        path=dockerfile_path,
        tag=image_name,
        rm=True,
    )
    for log in build_logs: # Print the build logs for debugging purposes
        print(log.get('stream', '').strip())
    print(f'Docker image {image_name} created successfully.')

def setup_node_red(client, volume_name, dir, url, email):
    # Clean the volume for the new user
    volume = client.volumes.get(volume_name)
    volume.remove()
    client.volumes.create(volume_name)
    # Set the username and password for the node-red container
    # Generate bcrypt hash from the user email
    hashed_password = bcrypt.hashpw(email.encode(), bcrypt.gensalt()).decode()
    # Copy the default settings file
    settings_default_file = os.path.join(dir, 'settings_default.js')
    with open(settings_default_file, 'r') as file:
        js_content = file.read()
    # Use regular expressions to find and replace the username, password, admin URL, and node URL
    username_pattern = r'username:\s*"[^"]*"'
    password_pattern = r'password:\s*"[^"]*"'
    admin_url_pattern = r'httpAdminRoot:\s*"[^"]*"'
    node_url_pattern = r'httpNodeRoot:\s*"[^"]*"'
    new_username_line = f'username: "{email}"'
    new_password_line = f'password: "{hashed_password}"'
    new_admin_url_line = f'httpAdminRoot: "{url}"'
    new_node_url_line = f'httpNodeRoot: "{url}"'
    js_content = re.sub(username_pattern, new_username_line, js_content)
    js_content = re.sub(password_pattern, new_password_line, js_content)
    js_content = re.sub(admin_url_pattern, new_admin_url_line, js_content)
    js_content = re.sub(node_url_pattern, new_node_url_line, js_content)
    # Write the modified content in a settings.js file
    settings_file = os.path.join(dir, 'settings.js')
    with open(settings_file, 'w') as file:
        file.write(js_content)

# Import lab config from Config object
server_name = Config.labs_config['server_name']
mounting = Config.labs_config['mountings'][0]
lab_duration = mounting['duration'] # in minutes
cam_url = mounting.get('cam_url', '')
lab_port = mounting['host_port']
lab = Config.labs_config['labs'][0]
lab_name = lab['lab_name']

nodered_dir = os.path.join(basedir, os.pardir, 'node-red')
default_volume = {'/dev/bus/usb': {'bind': '/dev/bus/usb', 'mode': 'rw'}}
lab_volumes = default_volume.update(lab.get('volumes', {}))

# Create docker lab image if not exists
client = docker.from_env()
lab_image_name = f'{lab_name.lower()}:latest'
try:
    client.images.get(lab_image_name)
    print(f'Docker image {lab_image_name} already exists.')
except docker.errors.ImageNotFound:
    lab_dockerfile_path = os.path.join(basedir, os.pardir)
    create_docker_image(lab_image_name, lab_dockerfile_path)

# Create or pull images in extra_containers
extra_containers = lab.get('extra_containers', [])
for container in extra_containers:
    image_name = container['image']
    try:
        client.images.get(image_name)
        print(f'Docker image {image_name} already exists.')
    except docker.errors.ImageNotFound:
        if container['name'] == 'node-red':
            # Create the node-red image
            create_docker_image(image_name, nodered_dir)
        else:
            print(f'Pulling Docker image {image_name}. Be patient, this will take a while...')
            client.images.pull(image_name)
            print(f'Docker image {image_name} pulled successfully.')
    
    # Create network 
    network_name = container['network']
    try:
        client.networks.get(network_name)
        print(f'Docker network {network_name} already exists.')
    except docker.errors.NotFound:
        print(f'Creating Docker network {network_name}.')
        client.networks.create(network_name)
        print(f'Docker network {network_name} created successfully.')

    # Create volumes
    volumes = container.get('volumes', {})
    for volume_name in volumes.keys():
        # Check if volume_name not starts with '/', so it is a volume and not a path
        if not volume_name.startswith('/'):
            try:
                client.volumes.get(volume_name)
                print(f'Docker volume {volume_name} already exists.')
            except docker.errors.NotFound:
                print(f'Creating Docker volume {volume_name}.')
                client.volumes.create(volume_name)
                print(f'Docker volume {volume_name} created successfully.')

print('All Docker images, networks and volumes are ready.')

# Docker environment variables
user_email = 'admin@email.com'
end_time = datetime.now(timezone.utc) + timedelta(minutes=lab_duration)
docker_env = {
    'SERVER_NAME': server_name,
    'LAB_NAME': lab_name,
    'USER_EMAIL': user_email,
    'USER_ID': 1,
    'END_TIME': end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
    'CAM_URL': cam_url,
}

containers = []
# Start the extra containers
for extra_container in extra_containers:
    if extra_container['name'] == 'node-red':
        nodered_url = f'/{server_name}/{lab_name}/nodered' # don't put the trailing slash
        volume_name = list(extra_container['volumes'].keys())[0] # e.g. 'integration_lab_vol'
        setup_node_red(client, volume_name, nodered_dir, nodered_url, user_email)

    container_extra = client.containers.run(
                    extra_container['image'], 
                    name=extra_container['name'],
                    detach=True, 
                    remove=True,
                    ports=extra_container['ports'],
                    volumes=extra_container.get('volumes', {}),
                    network=extra_container.get('network', ''),
                    command=extra_container.get('command', ''))
    containers.append(container_extra)

# Run the lab container
container_lab = client.containers.run(
                lab_image_name, 
                detach=True, 
                remove=True,
                privileged=True,
                ports={'8000/tcp': ('0.0.0.0', lab_port)}, 
                volumes=lab_volumes,
                environment=docker_env)
containers.append(container_lab)

stop_container = StopContainersTask(containers, end_time)
stop_container.start()


# Get the Raspberry pi IP address
hostname = subprocess.check_output(['hostname', '-I']).decode("utf-8").split()[0]
container_url = f'http://{hostname}:{lab_port}/{server_name}/{lab_name}/'
print(f'The container is running at {container_url} during {lab_duration} minutes.')

# Stop the containers when the program exits by pressing Ctrl+C
def exit_handler():
    # Check if the containers are still running
    for container in containers:
        try:
            container.stop()
        except:
            pass

atexit.register(exit_handler)



