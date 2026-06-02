# The way Charlette was able to run this

I have windows 10

# Neccesary to enter Ubuntu and run the other README.md in Indexer/

cd /mnt/c/Users/oconn/OneDrive/Documents/ucr_school_stuff/CS172_Web_Crawler
code .

# Might have to install these because venv issues

pip install scrapy
pip install pandas
pip install flask
pip install dos2unix

# Might be a windows/ubuntu issue so might have to install this 

dos2unix scripts/indexer.sh

# Other changes I made to the code for it to work

Indexer/searcher.py --- Check lines 145 - 149

# Follow the steps in the README.md in Indexer/ for building index

python -m flask --app frontend.app:app run --debug
