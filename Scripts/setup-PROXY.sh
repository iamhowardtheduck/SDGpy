# DELETE Pre-Configured logs-proxysg.log templates
curl -X DELETE "http://localhost:30920/_index_template/logs-proxysg.log" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "http://localhost:30920/_component_template/logs-proxysg.log@package" -H "Content-Type: application/json" -u "sdg:changeme"

# Recreate them in your image
curl -X PUT "http://localhost:30920/_component_template/logs-proxysg.log@package" -H "Content-Type: application/json" -u "sdg:changeme" -d @/root/SDGpy/Component-Templates/logs-proxysg.log.json
curl -X PUT "http://localhost:30920/_index_template/logs-proxysg.log" -H "Content-Type: application/json" -u "sdg:changeme" -d @/root/SDGpy/Index-Templates/logs-proxysg.log.json

# Begin data generation
# Begin data generation
python3 -m venv venv && source venv/bin/activate
pip install -r /root/SDGpy/requirements.txt
python /root/SDGpy/sdg.py /root/SDGpy/Tracks/saife-proxy.yml
