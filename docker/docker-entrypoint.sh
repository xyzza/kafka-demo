#!/usr/bin/env sh

set -e

case "$1" in
    api)
        echo "Starting application..."
        exec uvicorn --host 0.0.0.0 --port ${API_HTTP_PORT:-8000} --factory svc.app:create_app
        ;;
    worker)
        echo "Starting worker..."
        exec uvicorn --host 0.0.0.0 --port ${API_HTTP_PORT:-8008} --factory svc.app_worker:create_app
        ;;
    makemigration)
        shift
        exec ./makemigration.sh "$@"
        ;;
    migrate)
        shift
        exec alembic upgrade head
        ;;
    downgrade)
        shift
        exec alembic downgrade -1
        ;;
    tests)
        exec pytest tests -v
        ;;
    coverage)
        echo "running tests..."
        coverage run -m pytest -v -s tests
        echo "coverage report..."
        coverage report
        ;;
    analyze)
        echo "flake8..."
        flake8 svc tests
        echo "bandit..."
        bandit -c pyproject.toml -r svc
        echo "mypy..."
        mypy svc --show-error-codes --ignore-missing-imports
        echo "isort..."
        isort --check-only --diff svc tests migrations
        echo "black..."
        black --check svc tests migrations
        ;;
    mypy)
        echo "mypy..."
        mypy svc tests --show-error-codes --ignore-missing-imports
        ;;
    format)
        echo "pautoflake..."
        pautoflake -r svc tests migrations
        echo "isort..."
        isort svc tests migrations
        echo "black..."
        black svc tests migrations
        ;;
    *)
        exec "$@"
esac
