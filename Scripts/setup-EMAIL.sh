# DELETE Pre-Configured logs-ti_abusech.malware templates
curl -X DELETE "http://localhost:30920/_index_template/logs-ti_abusech.malware" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "http://localhost:30920/_index_template/logs-ti_abusech.malwarebazaar" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "http://localhost:30920/_component_template/logs-ti_abusech.malware@package" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "http://localhost:30920/_component_template/logs-ti_abusech.malwarebazaar@package" -H "Content-Type: application/json" -u "sdg:changeme"

# Recreate them in your image
curl -X PUT "http://localhost:30920/_component_template/logs-ti_abusech.malware@package" -H "Content-Type: application/json" -u "sdg:changeme" -d @/root/SDGpy/Component-Templates/logs-ti_abusech.malware.json
curl -X PUT "http://localhost:30920/_index_template/logs-ti_abusech.malware" -H "Content-Type: application/json" -u "sdg:changeme" -d @/root/SDGpy/Index-Templates/logs-ti_abusech.malware.json
curl -X PUT "http://localhost:30920/_index_template/logs-email.filter" -H "Content-Type: application/json" -u "sdg:changeme" -d @/root/SDGpy/Index-Templates/logs-email.filter.json


# Rollover existing index in order to inherit new settings without any garbage data
#curl -X POST "http://localhost:30920/logs-windows.sysmon_operation-default/_rollover" -u "sdg:changeme"

# Begin data generation
python3 -m venv venv && source venv/bin/activate
pip install -r /root/SDGpy/requirements.txt
python3 /root/SDGpy/sdg.py /root/SDGpy/Tracks/saife-email.yml
