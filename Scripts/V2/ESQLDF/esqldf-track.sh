# Begin data generation
#
# identity.py must sit next to sdg.py (/home/elastic/SDGpy/identity.py) — the
# esqldf.yml track's employee_* field types depend on it. It is pure stdlib,
# so requirements.txt is unchanged.
if [ ! -f /home/elastic/SDGpy/identity.py ]; then
  echo "ERROR: /home/elastic/SDGpy/identity.py is missing." >&2
  echo "       The esqldf.yml track needs it for employee-coherent IPs/names." >&2
  exit 1
fi

python3 -m venv venv && source venv/bin/activate
pip install -r /home/elastic/SDGpy/requirements.txt
python3 /home/elastic/SDGpy/Scripts/V2/ESQLDF/sdg.py /home/elastic/SDGpy/Tracks/V2/esqldf-V2.yml
