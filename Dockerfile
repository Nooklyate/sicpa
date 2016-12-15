FROM python:3.4.5

ENV PORT=8001

# create directory to put app in
RUN mkdir /app
WORKDIR /app

# install requirements & create && activate virtual env
COPY requirements.txt /app

# if you ever need virtual env, install it via pip then use it as normal:
# RUN pip install virtualenv && virtualenv env && source env/bin/activate
RUN pip install -r requirements.txt

# copy sources
COPY . /app

EXPOSE $PORT
CMD [ "flask", "run", "--host", "0.0.0.0", "--port", "8001" ]
