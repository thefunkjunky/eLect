# eLect
## eLect - an online elections platform, with future Blockchain support

(Note: This is a project I started over a year ago to teach myself how to program, 
and is currently still a work in progress.)  

One only has to look at some grim statistics to know that the state of democracy is failing on almost every front,
including the act of voting itself.  Voter turnout is abysmal, whatever voters do turn out are routinely disenfranchised by discriminatory and arcane laws, inadequate polling stations and resources, and easily hackable voting machines and election software,  with little to no accountability in regards to the software, hardware, and source code, or verifiable paper trails for the results.

This software will attempt to solve a few problems: the problem of voter turnout and ease of registration, the problem of voter identification, and the problem of security and accountability for online election systems.  The proposed solutions will rely on the power and transparency of distributed ledgers, or blockchain technology. It will also attempt to unify election systems under an easy-to-use and secure system, both for creating and managing elections, but of also of voter registration, user participation and communication/community building, and clean, simple, and effective UX design.  You know, someday.  

In the meantime, the project can be cloned and run in its current state by first cloning the repository:  
```
git clone git@github.com:thefunkjunky/eLect.git
``` 
  or  
  
```git clone https://github.com/thefunkjunky/eLect.git```

You will need PostgreSQL 9.4+ (preferably 9.5) installed, set up, and running, and two databases created: one for the normal eLect project (ex. "eLect-db"), and a test database with the same name with "-test" appended (ex. "eLect-db-test").  See online documentation for instructions on how to do this on your system.  

create a python3 virtual environment in the project folder  
```python3 -m venv env```

change source to virtual environment  
```source env/bin/activate```

pip install requirements (make sure you have the python libs and compilers you need to make and install python3 packages)  
```pip install -r requirements.txt```

set up database access via wizard:  
```python config_wizard.py```

populate database (default database used : *-test):  
```python run.py seed_db```

run flask server/project  
```python run.py run```

run tests:  
```
nosetests 
```    

More info to come as project is fleshed out.









