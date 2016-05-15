import json
import getpass


# Using json config file to avoid  uploading passwords to git, and dealing with different
# PostgreSQL usernames on different machines

def main():
	# I was taught to use this as an environment variable, but I don't
	# like that for some reason.  So I'm just doing it here.  This is 
	# probably more insecure though, might want to look into that.
	secret_env_key = ""

	print("Configuring project variables configuration file.")
	db_name = input('Please enter SQL database name.> ')
	username = input('Please enter db admin username.> ')
	password = getpass.getpass('Enter admin password:> ')
	host = input("Please enter database host server (leave blank for default localhost) > ")
	port = input("Please enter port number (leave blank for default port 5432.> ")
	if host == "": host = "127.0.0.1"
	if port == "": port = 5432


	conf_dict = {
	"dbname": db_name,
	"user": username,
	"password": password,
	"host": host,
	"port": port,
	"secret_key": secret_env_key
	}

	filename = "main_config_variables.json"
	with open(filename, 'w') as cfg:
		cfg.write(json.dumps(conf_dict, 
			sort_keys=True, 
			indent=4, 
			separators=(',', ': ')
			)
		)

	# Change dbname to the test db and write test config file
	conf_dict["dbname"] = db_name + "-test"
	filename = "test_config_variables.json"
	with open(filename, 'w') as cfg:
		cfg.write(json.dumps(conf_dict, 
			sort_keys=True, 
			indent=4, 
			separators=(',', ': ')
			)
		)

if __name__ == '__main__':
	main()

