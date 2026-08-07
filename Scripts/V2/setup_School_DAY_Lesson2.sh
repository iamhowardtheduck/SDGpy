# DELETE Pre-Configured templates
curl -X DELETE "https://es.elastic.lab:443/_index_template/logs-windows.sysmon_operational" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "https://es.elastic.lab:443/_component_template/logs-windows.sysmon_operational@package" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "https://es.elastic.lab:443/_index_template/logs-network_traffic.dns" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "https://es.elastic.lab:443/_component_template/logs-network_traffic.dns@package" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "https://es.elastic.lab:443/_index_template/logs-proxysg.log" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "https://es.elastic.lab:443/_component_template/logs-proxysg.log@package" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "https://es.elastic.lab:443/_index_template/logs-ti_abusech.malware" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "https://es.elastic.lab:443/_index_template/logs-ti_abusech.malwarebazaar" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "https://es.elastic.lab:443/_component_template/logs-ti_abusech.malware@package" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "https://es.elastic.lab:443/_component_template/logs-ti_abusech.malwarebazaar@package" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "https://es.elastic.lab:443/_index_template/logs-netflow.log" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "https://es.elastic.lab:443/_component_template/logs-netflow.log@package" -H "Content-Type: application/json" -u "sdg:changeme"


# Create an updated ingest pipeline for the custom logs
curl -X PUT "https://es.elastic.lab:443/_ingest/pipeline/logs@custom" -H "Content-Type: application/x-ndjson" -u "sdg:changeme" -d @/home/elastic/SDGpy/Ingest-Pipelines/logs@custom.json

# Recreate them in your image
curl -X PUT "https://es.elastic.lab:443/_component_template/logs@settings" -H "Content-Type: application/json" -u "sdg:changeme" -d @/home/elastic/SDGpy/Component-Templates/logs@settings.json
curl -X PUT "https://es.elastic.lab:443/_index_template/logs" -H "Content-Type: application/json" -u "sdg:changeme" -d @/home/elastic/SDGpy/Index-Templates/logs.json
curl -X PUT "https://es.elastic.lab:443/_component_template/logs-network_traffic.dns@package" -H "Content-Type: application/json" -u "sdg:changeme" -d @/home/elastic/SDGpy/Component-Templates/logs-network_traffic.dns.json
curl -X PUT "https://es.elastic.lab:443/_index_template/logs-network_traffic.dns" -H "Content-Type: application/json" -u "sdg:changeme" -d @/home/elastic/SDGpy/Index-Templates/logs-network_traffic.dns.json
curl -X PUT "https://es.elastic.lab:443/_component_template/logs-proxysg.log@package" -H "Content-Type: application/json" -u "sdg:changeme" -d @/home/elastic/SDGpy/Component-Templates/logs-proxysg.log.json
curl -X PUT "https://es.elastic.lab:443/_index_template/logs-proxysg.log" -H "Content-Type: application/json" -u "sdg:changeme" -d @/home/elastic/SDGpy/Index-Templates/logs-proxysg.log.json
curl -X PUT "https://es.elastic.lab:443/_component_template/logs-ti_abusech.malware@package" -H "Content-Type: application/json" -u "sdg:changeme" -d @/home/elastic/SDGpy/Component-Templates/logs-ti_abusech.malware.json
curl -X PUT "https://es.elastic.lab:443/_index_template/logs-ti_abusech.malware" -H "Content-Type: application/json" -u "sdg:changeme" -d @/home/elastic/SDGpy/Index-Templates/logs-ti_abusech.malware.json
curl -X PUT "https://es.elastic.lab:443/_index_template/logs-email.filter" -H "Content-Type: application/json" -u "sdg:changeme" -d @/home/elastic/SDGpy/Index-Templates/logs-email.filter.json
curl -X PUT "https://es.elastic.lab:443/_component_template/logs-netflow.log@package" -H "Content-Type: application/json" -u "sdg:changeme" -d @/home/elastic/SDGpy/Component-Templates/logs-netflow.log.json
curl -X PUT "https://es.elastic.lab:443/_index_template/logs-netflow.log" -H "Content-Type: application/json" -u "sdg:changeme" -d @/home/elastic/SDGpy/Index-Templates/logs-netflow.log.json
curl -X PUT "https://es.elastic.lab:443/_component_template/logs-windows.sysmon_operational@package" -H "Content-Type: application/json" -u "sdg:changeme" -d @/home/elastic/SDGpy/Component-Templates/logs-windows.sysmon-operational.json
curl -X PUT "https://es.elastic.lab:443/_index_template/logs-windows.sysmon_operational" -H "Content-Type: application/json" -u "sdg:changeme" -d @/home/elastic/SDGpy/Index-Templates/logs-windows.sysmon_operational.json


# Begin data generation
python3 -m venv venv && source venv/bin/activate
pip install -r /home/elastic/SDGpy/requirements.txt
python3 /home/elastic/SDGpy/sdg.py /home/elastic/SDGpy/Tracks/V2/schoolday_all_lesson2.yml
