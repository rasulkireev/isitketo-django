serve:
	docker-compose up -d --build
	docker compose logs -f backend

shell:
	docker compose run --rm backend python ./manage.py shell_plus --ipython

prod-shell:
	./scripts/prod-shell.sh

prod-generate-ai-images:
	./scripts/generate_ai_images.sh
