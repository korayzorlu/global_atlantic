## Instructions

### Project Setup

- Pull the repository
- Create a virtual environment
    - VS Code:
        - Terminal -> New Terminal
 
              cmd
              py -m venv venv
              venv\scripts\activate
    - PyCharm:
        - File -> Settings / Project: michoapp / Python Interpreter
        - Click settings icon and select Add...
        - Click OK
        - Close existing terminals and open a new terminal
        - Check if the (venv) word exist at the start of the terminal line (to check if the venv running)
- Install the requirements of the project:
    - Open the terminal:

          pip install -r requirements.txt
- Create a duplicate of ".env.example" file with ".env" name in the root directory
- (Optional) You can change the SECRET_KEY (https://stackoverflow.com/a/53144229/14506165)
- Create a duplicate of "development.py.example" file with "development.py" name in the settings directory
- Add your database properties to core/settings/development.py
- Check the project if it is running correctly:
    - Open the terminal:
    
          python manage.py runserver
    - Stop the process and contact with @nurucar if you deal with any problem
- Open the terminal:

      python manage.py makemigrations
      python manage.py migrate
      python manage.py loaddata country city currency
      python manage.py createsuperuser
      python manage.py runserver
- If you encountered any problem during the instructions, please restart from top
- Contact with @nurucar if the problem persists

- Open Django Admin Interface:
    - Open Reasons page:
        Add all reason as unique
    - Open Claim reasons page:
        Add all claim reasons as unique 
    - Open Claim results page:
        Add all claim results as unique

### Database Backup & Restore

- We will use PostgreSQL binaries, thus we need to add them to the system environments:
    - This PC > Properties > Advanced System Settings > Environment Variables:
        - Double-click to the "Path" variable inside the "User variables for ..."
        - Click the "New" button
        - Enter this path "C:\Program Files\PostgreSQL\13\bin" (the "13" depends on the version of the installed PostgreSQL in your system)
        - Close all the windows by clicking the OK buttons on them

#### Backup

- Let's say you have:
    - The name of the file to extract: backup_file_2021.sql
    - Database username: postgres
    - Source database name: michoapp
- Open the terminal:

       pg_dump -h 127.0.0.1 -U postgres -T django_migrations michoapp > backup_file_2021.sql
- Additionally, you can backup the database with clean parameter:
    
       pg_dump -h 127.0.0.1 -U postgres -c -T django_migrations michoapp > backup_file_2021_clean.sql
- Enter your password
- You are done

#### Restore
WARNING: Be sure you have a full match backup file to the current models of the project!

- Let's say you have:
    - Backup filename: backup_file_2021.sql
    - Database username: postgres
    - Target database name: michoapp
- Open the terminal:

       python manage.py makemigrations
       psql -h 127.0.0.1 -U postgres michoapp < backup_file_2021.sql
       python manage.py migrate --fake
- Enter your password
- You are done after successfully following the complete above steps.

---
