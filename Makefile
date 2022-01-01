install:
	poetry install

run:
	poetry run python api_client.py

lint:
	poetry run black .
