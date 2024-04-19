#!/bin/sh

set -e

celery -A psmproject.celery worker -l INFO --concurrency 2
