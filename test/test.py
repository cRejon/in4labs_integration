import os
import subprocess
import threading
import time
from datetime import datetime, timedelta
import atexit

import docker

from test_config import Config


# Class to stop the containers when the time is up
class StopContainersTask(threading.Thread):
     def __init__(self, containers, end_time):
         super(StopContainersTask, self).__init__()
         self.containers = containers
         self.end_time = end_time
 
     def run(self):
        remaining_secs = (end_time - datetime.now()).total_seconds()
        time.sleep(remaining_secs)
        for container in self.containers:
            container.stop()
        print('Lab containers stopped.')


# Import lab config from Config object
lab_duration = Config.labs_config['duration']
lab = Config.labs_config['labs'][0]
lab_name = lab['lab_name']
lab_image_name = f'{lab_name.lower()}:latest'
host_port = lab['host_port']

# Export DOCKER_HOST environment variable to run in rootless mode
os.environ['DOCKER_HOST'] = 'unix:///run/user/1000/docker.sock'

# Create docker image if not exists
client = docker.from_env()
try:
    client.images.get(lab_image_name)
    print(f'Docker image {lab_image_name} already exists.')
except docker.errors.ImageNotFound:
    print(f'Creating Docker image {lab_image_name}. Be patient, this will take a while...')
    basedir = os.path.abspath(os.path.dirname(__file__))
    dockerfile_path = os.path.join(basedir, os.pardir)
    image, build_logs = client.images.build(
        path=dockerfile_path,
        tag=lab_image_name,
        rm=True,
    )
    for log in build_logs: # Print the build logs for debugging purposes
        print(log.get('stream', '').strip())
    print(f'Docker image {lab_image_name} created successfully.')

# Pull images in extra_containers
extra_containers = lab.get('extra_containers', [])
for container in extra_containers:
    image_name = container['image']
    try:
        client.images.get(image_name)
        print(f'Docker image {image_name} already exists.')
    except docker.errors.ImageNotFound:
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

print('All Docker images and networks are ready.')

# Get the Raspberry pi IP address
hostname = subprocess.check_output(['hostname', '-I']).decode("utf-8").split()[0]
nodered_nat_port = lab['extra_containers'][0]['nat_port']

# Docker environment variables
end_time = datetime.now() + timedelta(minutes=lab_duration)
docker_env = {
    'USER_EMAIL': 'admin@email.com',
    'USER_ID': 1,
    'END_TIME': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
    'CAM_URL': lab.get('cam_url', ''),
    'NODE_RED_URL': f'http://{hostname}:{nodered_nat_port}',
}

# Run the lab container
containers = []
container_lab = client.containers.run(
                lab_image_name, 
                detach=True, 
                remove=True,
                privileged=True,
                volumes={'/dev/bus/usb': {'bind': '/dev/bus/usb', 'mode': 'rw'}},
                ports={'8000/tcp': ('0.0.0.0', host_port)}, 
                environment=docker_env)
containers.append(container_lab)

# Start the extra containers
for extra_container in extra_containers:
    container_extra = client.containers.run(
                    extra_container['image'], 
                    name=extra_container['name'],
                    detach=True, 
                    remove=True,
                    network=extra_container['network'],
                    ports=extra_container['ports'],
                    command=extra_container.get('command', ''))
    containers.append(container_extra)

stop_container = StopContainersTask(containers, end_time)
stop_container.start()


lab_url = f'http://{hostname}:{host_port}'
print(f'The container is running at {lab_url} during {lab_duration} minutes.')

# Stop the containers when the program exits by pressing Ctrl+C
def exit_handler():
    for container in containers:
        container.stop()
    print('Lab containers stopped.')

atexit.register(exit_handler)



