# reverse_backdoor
Simple reverse backdoor utility, that uses sockets to communicate.

How to use:

Run rev_bd_listener.py using command below:
python3 rev_bd_listener.py

Change IP address to the one you wish to connect to in rev_bd_victim.py.

Run rev_bd_victim.py on the victim's computer:
python3 rev_bd_victim.py

Now you can execute system commands on victim's PC from listener's PC, download files from the victim, upload files to the victim.

Available custom commands:
download <path_to_file_on_victim>
upload <path_to_file_on_listener>
cd
quit
