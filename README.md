# student-intern-organiser

This is a way for WEHI to organise the Research Software Engineer Student Internship program
# Installation
To begin, please follow the steps below for installing Python and setting up the virtual environment:

## Install Python
Download the latest version of Python from the official website.
[Download Here](https://www.python.org/)

# Windows
Follow the installation instructions provided, ensuring that Python is added to the system PATH.
## Install virtualenv
Open the command prompt.
Run the following command to install virtualenv:
```
pip install virtualenv
```
## Create a virtual environment
Open the command prompt in the desired project directory/folder.
Create a new virtual environment by running the following command:

```
virtualenv .env
```
## Activate the virtual environment
Run the following command to activate the virtual environment:
```
.\.env\Scripts\activate
```
## Run the application
Start the Flask application by running the following command:
```
flask run
```

# MacOS/Linux
Open Terminal
## install virtualenv
```
pip install virtualenv
```
## Create a virtual environment
```
python3 -m venv venv
```
## Activate the virtual environment
```
source venv/bin/activate
```
## Install Flask
```
pip install flask
```

>Make sure the virtual environment is activated.

## Run the Flask application
```
flask run
```

>Note: Remember to deactivate the virtual environment once you have finished using the application. Simply run the command
 ``` 
 deactivate
 ``` 
in the terminal to deactivate the virtual environment.

>We hope this documentation helps you in setting up and running the Student Intern Organiser effectively. 

If you have any further questions or issues, please don't hesitate to reach out for assistance.
