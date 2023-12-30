FROM python:3.11

# prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# ensure Python output is sent directly to the terminal without buffering
ENV PYTHONUNBUFFERED 1

# Set the working directory to /usr/src/app/
WORKDIR /usr/src/app

RUN pip install --upgrade pip
# Copy and Install any needed packages specified in requirements.txt
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# Copy the entrypoint.sh file to test before deployment
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# Copy the current directory contents into the container at /usr/src/app/
COPY . /usr/src/app/


ENTRYPOINT ["/usr/src/app/entrypoint.sh"]