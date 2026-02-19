# Begin data generation
python3 -m venv venv && source venv/bin/activate
pip install -r /root/SDGpy/requirements.txt
python3 /root/SDGpy/sdg.py /root/SDGpy/Tracks/schoolday_all_lesson3.yml
