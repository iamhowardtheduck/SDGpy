# DELETE Pre-Configured Windows templates
curl -X DELETE "https://es.elastic.lab:443/_index_template/logs-network_traffic.dns" -H "Content-Type: application/json" -u "sdg:changeme"
curl -X DELETE "https://es.elastic.lab:443/_component_template/logs-network_traffic.dns@package" -H "Content-Type: application/json" -u "sdg:changeme"

# Recreate them in your image
curl -X PUT "https://es.elastic.lab:443/_component_template/logs-network_traffic.dns@package" -H "Content-Type: application/json" -u "sdg:changeme" -d @/home/elastic/SDGpy/Component-Templates/logs-network_traffic.dns.json
curl -X PUT "https://es.elastic.lab:443/_index_template/logs-network_traffic.dns" -H "Content-Type: application/json" -u "sdg:changeme" -d @/home/elastic/SDGpy/Index-Templates/logs-network_traffic.dns.json


# Begin data generation
python3 -m venv venv && source venv/bin/activate
pip install -r /home/elastic/SDGpy/requirements.txt
python3 /home/elastic/SDGpy/sdg.py /home/elastic/SDGpy/Tracks/V2/saife-dns.yml
