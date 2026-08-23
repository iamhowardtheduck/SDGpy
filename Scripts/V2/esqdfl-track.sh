# Begin data generation
python3 -m venv venv && source venv/bin/activate
pip install -r /root/SDGpy/requirements.txt
python3 /root/SDGpy/sdg.py /root/SDGpy/Tracks/V2/esqldf.yml
