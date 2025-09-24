#!/usr/bin/env bash
# Script rápido para crear venv e iniciar la app Flask (desde la raíz del proyecto)
set -e
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd backend
python3 app.py
