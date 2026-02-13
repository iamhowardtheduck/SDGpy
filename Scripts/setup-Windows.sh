# DELETE Pre-Configured Windows templates
curl -X DELETE "http://localhost:30920/_index_template/logs-netflow.log" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "http://localhost:30920/_component_template/logs-netflow.log@package" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "http://localhost:30920/_index_template/logs-windows.sysmon_operational" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "http://localhost:30920/_component_template/logs-windows.sysmon_operational@package" -H "Content-Type: application/json" -u "sdg:changeme"

# DELETE associated datastream if present
#curl -X DELETE "http://localhost:30920//_data_stream/logs-windows.sysmon_operational-default" -u "sdg:changeme"

# Create an updated ingest pipeline for the custom logs
curl -X PUT "http://localhost:30920/_ingest/pipeline/logs@custom" -H "Content-Type: application/x-ndjson" -u "sdg:changeme" -d @/root/SDGpy/Ingest-Pipelines/logs@custom.json

# Recreate them in your image
curl -X PUT "http://localhost:30920/_component_template/logs-netflow.log@package" -H "Content-Type: application/json" -u "sdg:changeme" -d @/root/SDGpy/Component-Templates/logs-netflow.log.json
curl -X PUT "http://localhost:30920/_index_template/logs-netflow.log" -H "Content-Type: application/json" -u "sdg:changeme" -d @/root/SDGpy/Index-Templates/logs-netflow.log.json
curl -X PUT "http://localhost:30920/_component_template/logs-windows.sysmon_operational@package" -H "Content-Type: application/json" -u "sdg:changeme" -d @/root/SDGpy/Component-Templates/logs-windows.sysmon-operational.json
curl -X PUT "http://localhost:30920/_index_template/logs-windows.sysmon_operational" -H "Content-Type: application/json" -u "sdg:changeme" -d @/root/SDGpy/Index-Templates/logs-windows.sysmon_operational.json
curl -X PUT "http://localhost:30920/_component_template/logs@settings" -H "Content-Type: application/json" -u "sdg:changeme" -d @/root/SDGpy/Component-Templates/logs@settings.json
curl -X PUT "http://localhost:30920/_index_template/logs" -H "Content-Type: application/json" -u "sdg:changeme" -d @/root/SDGpy/Index-Templates/logs.json

# Create Datastream:
curl -X PUT "http://localhost:30920/_data_stream/logs-windows.sysmon_operational-default" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X PUT "http://localhost:30920/_data_stream/logs-netflow.log-default" -H "Content-Type: application/json" -u "sdg:changeme"

# Rollover existing index in order to inherit new settings without any garbage data
#curl -X POST "http://localhost:30920/logs-windows.sysmon_operation-default/_rollover" -u "sdg:changeme"

# Begin data generation
python3 -m venv venv && source venv/bin/activate
pip install -r /root/SDGpy/requirements.txt
python3 /root/SDGpy/sdg.py /root/SDGpy/Tracks/saife-windows.yml
