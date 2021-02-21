release: ./deploy/store_certs.sh

web: uvicorn main:app --host=0.0.0.0 --port=${PORT:-5000}
receiver: python receiver.py
