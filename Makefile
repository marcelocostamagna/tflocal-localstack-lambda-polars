.PHONY: build
build:
	@docker compose build

.PHONY: up
up:
	@docker compose up -d

.PHONY: down
down:
	@docker compose down -v

.PHONY: lambda_pkgs
lambda_pkgs:
	pip install -r lambdas/convert-parquet-silver/requirements.txt --target lambdas/convert-parquet-silver/convert-parquet-silver-package
	cp ./lambdas/convert-parquet-silver/handler.py ./lambdas/convert-parquet-silver/convert-parquet-silver-package
	sh -c "cd lambdas/convert-parquet-silver/convert-parquet-silver-package && zip -r ../convert-parquet-silver-package.zip ."
	rm -r lambdas/convert-parquet-silver/convert-parquet-silver-package
	pip install -r lambdas/cp-landing-bronze/requirements.txt --target lambdas/cp-landing-bronze/cp-landing-bronze-package
	cp ./lambdas/cp-landing-bronze/handler.py ./lambdas/cp-landing-bronze/cp-landing-bronze-package
	sh -c "cd lambdas/cp-landing-bronze/cp-landing-bronze-package && zip -r ../cp-landing-bronze-package.zip ."
	rm -r lambdas/cp-landing-bronze/cp-landing-bronze-package
	

.PHONY: ingest_data
ingest_data:
	@docker compose run \
	-v $(shell pwd)/apps/flights-generator:/app \
	--entrypoint "python /app/flights-generator.py" \
	flights_generator


  