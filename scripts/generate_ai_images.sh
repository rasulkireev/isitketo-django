ssh -t root@138.201.126.181 'docker exec -it $(docker ps --filter "name=srv-captain--isitketo" --format "{{.ID}}" | head -n1) python manage.py generate_ai_image_for_product'
