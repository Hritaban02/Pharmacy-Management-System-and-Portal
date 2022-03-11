# Pharmacy-Management-System-and-Portal

> The pharmacy management system and portal is built 
> to efficiently manage the inventory of the pharmacy as well as 
> providing the customers with a online portal using which 
> they can easily view the pharmacy at a glance without physically visiting it.

# DEMO

Youtube Video demonstrating the features of the Web Application in detail.

[![Demo for the Project](https://img.youtube.com/vi/xm-PVOJMb5I/maxresdefault.jpg)](https://www.youtube.com/watch?v=xm-PVOJMb5I)

# SLIDESHOW FOR THE PROJECT

Youtube Video demonstrating the features of the Web Application in a silent slideshow.

[![Slideshow for the Project](https://img.youtube.com/vi/wupJJxW-5ns/maxresdefault.jpg)](https://www.youtube.com/watch?v=wupJJxW-5ns)

# Steps to set up the server and connect to a database

### Step 1 - Download

Download the source folder onto your Desktop or PC.

### Step 2 - Setup the python environment

Open the folder as a Project in any suitable IDE which supports [Python 3.10](https://www.python.org/downloads/)

### Step 3 - Open settings.py and connect to your database

Go to source/pmsp/pmsp/settings.py and looke for the following piece of code

```sh
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        # Type your database name here.
        'NAME': '<YOUR-DATABASE-NAME>',
        'USER': 'root',
        # Type your password here.
        'PASSWORD': '<YOUR-PASSWORD>',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}
```

Here change the ENGINE to your database type.
Refer to the [django docs](https://docs.djangoproject.com/en/4.0/ref/databases/) for more information.

Then type in your database name and password. Remember to change other parameters as per the requirement of your database.

### Step 3 - Change directory and Load all dependencies

In the terminal, execute the following commands.

```sh
cd pmsp
pip install -r requirements.txt
```

This will load all the required dependencies of the project.

### Step 4 - Make migrations, migrate and create superuser

After all dependencies are installed, set up the database models and create a superuser (admin).

```sh
python manage.py makemigrations accounts arrived_stocks home item medicine orders phone_number staff stock_requests vendor 
python manage.py migrate
pyhton manage.py createsuperuser
```

You will be prompted for username, email and password for the superuser. Enter the same and proceed.

### Step 5 - Run the server

Execute the following command to run the server and open the link in Google Chrome.

```sh
python manage.py runserver
```

You will get the base link of your web application. Open the link in Google Chrome. The front-end of this application has not been tested on other browsers.

### Step 6 - Log In as admin 

Upon opening the link, go to the login page using the Log In button.
Enter the credentials of the admin you had entered before.
Then you will be redirected to Django's user freindly database administration which has been customized by me.
Here you can create vendors, medicines and staff members.

This will populate the database to which you have connected.

# HAPPY CODING!!!
