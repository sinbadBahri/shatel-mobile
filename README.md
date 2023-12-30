Hi, my name is fuad. 
I used pytest for testing th project.

You can find my pytest configs in "setup.cfg" file.


**Requirements**

* pytest
* pytest-django


## How to run

Go to the project folder where you see "manage.py" and Dockerfile.

Run the docker-compose:

    $ sudo docker-compose up 

Tests start automaticly and after that development server starts at  http://0.0.0.0:8000/



Or

if you run tests without using docker-compose, you can always:
Install requirements first ...

    (venv) $ pip install -r requirements.txt

Then run tests using pytest cmd:
	(venv) $ pytest
	
	
You can find test files in path:'code_challenge_qa/tests'.
Thanks.   :)
