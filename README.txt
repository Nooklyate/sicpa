To build the image (the --tag argument is the tag of the image):
  docker build --tag=pw-flask .

To run interactively FOR DEBUGGING (the -i is interactive, -t stands for TTY
and the last argument is the tag name, as used above)
  docker run -i -t pw-flask /bin/bash

If you want to attach to an already running container, see this:
http://askubuntu.com/questions/505506/how-to-get-bash-or-ssh-into-a-running-container-in-background-mode
docker exec -i -t <jobid> /bin/bash

Once the image is built, you can run a container based off of it
(see https://docs.docker.com/engine/reference/run/ for more info):
  docker run -p "8000:8000" -e "FLASK_APP=app/hello.py" -e "LC_ALL=C.UTF-8" -e "LANG=C.UTF-8" pw-flask

To run on the server
  docker run -p "80:8000" -d --restart=unless-stopped -e "FLASK_APP=app/hello.py" -e "LC_ALL=C.UTF-8" -e "LANG=C.UTF-8" pw-flask

to run in dev, set flask_debug to 1:
REMEMBER TO CHANGE -v to ABSOLUTE PATH OF YOUR COMPUTER
# set default env vars
  docker run \
    -p "8000:8000" \
    -v "/Users/pweinkam/dev/pw-flask/app:/app/app" \
    -e "FLASK_APP=app/hello.py" \
    -e "LC_ALL=C.UTF-8" \
    -e "LANG=C.UTF-8" \
    -e "FLASK_DEBUG=1" \
    pw-flask

  -v local:remote mount volume
  -p maps the container port to a host port (container:host)
  (container is the one that is EXPOSE'd in the docker file, host is the port
  you put into your browser)

  use -d to detach when running in prod or in the background


docker ps
docker kill
docker logs [container id]
docker logs -f [container id] (to follow along, like tail)
