# DELETE Pre-Configured Windows templates
curl -X DELETE "http://localhost:30920/_index_template/logs-network_traffic.dns" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "http://localhost:30920/_component_template/logs-network_traffic.dns@package" -H "Content-Type: application/json" -u "sdg:changeme"

# Recreate them in your image
curl -X PUT "http://localhost:30920/_component_template/logs-network_traffic.dns@package" -H "Content-Type: application/json" -u "sdg:changeme" -d @/root/SDGpy/Component-Templates/logs-network_traffic.dns.json
curl -X PUT "http://localhost:30920/_index_template/logs-network_traffic.dns" -H "Content-Type: application/json" -u "sdg:changeme" -d @/root/SDGpy/Index-Templates/logs-network_traffic.dns.json


# Begin data generation
python3 -m venv venv && source venv/bin/activate
pip install -r /root/SDGpy/requirements.txt
python3 /root/SDGpy/sdg.py /root/SDGpy/Tracks/saife-dns.yml
