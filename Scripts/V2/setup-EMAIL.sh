# DELETE Pre-Configured logs-ti_abusech.malware templates
curl -X DELETE "https://es.elastic.lab:443/_index_template/logs-ti_abusech.malware" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "https://es.elastic.lab:443/_index_template/logs-ti_abusech.malwarebazaar" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "https://es.elastic.lab:443/_component_template/logs-ti_abusech.malware@package" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "https://es.elastic.lab:443/_component_template/logs-ti_abusech.malwarebazaar@package" -H "Content-Type: application/json" -u "sdg:changeme"

# Recreate them in your image
curl -X PUT "https://es.elastic.lab:443/_component_template/logs-ti_abusech.malware@package" -H "Content-Type: application/json" -u "sdg:changeme" -d @/home/elastic/SDGpy/Component-Templates/logs-ti_abusech.malware.json
curl -X PUT "https://es.elastic.lab:443/_index_template/logs-ti_abusech.malware" -H "Content-Type: application/json" -u "sdg:changeme" -d @/home/elastic/SDGpy/Index-Templates/logs-ti_abusech.malware.json
curl -X PUT "https://es.elastic.lab:443/_index_template/logs-email.filter" -H "Content-Type: application/json" -u "sdg:changeme" -d @/home/elastic/SDGpy/Index-Templates/logs-email.filter.json


# Rollover existing index in order to inherit new settings without any garbage data
#curl -X POST "https://es.elastic.lab:443/logs-windows.sysmon_operation-default/_rollover" -u "sdg:changeme"

# Begin data generation
python3 -m venv venv && source venv/bin/activate
pip install -r /home/elastic/SDGpy/requirements.txt
python3 /home/elastic/SDGpy/sdg.py /home/elastic/SDGpy/Tracks/V2/saife-email.yml
