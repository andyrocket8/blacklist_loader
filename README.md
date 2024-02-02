# Blacklist loader

## Purpose
Simple application for parsing IP addresses from the content of the folder to Blacklist application 

## Logic
You can specify several rules for different file types. 
For every rule:
1) All files from folder are matched with file mask pattern.
2) If file name matched file mask ("file_mask" option) then file is parsed with rule pattern (regex expression).  
   Both regex group (indexed as 0) and total matched regex are valid.
   
 
```
   Example:   
   
   Pattern with capturing group: 
   Some.address,([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})
   
   Pattern without capturing group
   [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}
   
```    
3) If some addresses are parsed they would saved in Blacklist application (/addresses/banned/add handle)
After processing file is moved to archive folder 

Every rule might have "check_value" option. If specified the application will check "pattern" with test value on application startup. 

## Usage
Please run main.py with yaml config file as the only command argument
Example: 
``` 
python main.py config.yml
```

## Configuration
Config file satisfies YAML format rules.

```
# Blacklist App connection options
blacklist:                                          
    uri: http://127.0.0.1:8000/addresses/banned/add   # URI of add method
    agent_name: Loader parser                         # Agent name 
    token:                                            # Specify if Blacklist App authorization is ON

source: /home/core/develop/secure/stuff/file_loader/files     # Folder to process 
archive: /home/core/develop/secure/stuff/file_loader/archive  # Folder to archive file after processing 

rules:  # Processing rules  
    - file_mask: "*.csv"    # File mask
      # Search pattern   
      pattern: .*Some.address,([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}).*
      # Value for checking on program startup
      check_value: Some address,95.85.116.174;1;3;3
    - file_mask: "*.banned"
      pattern: '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'
      check_value: <SomeAddress>200.25.254.193</SomeAddress>
    - ....
```
