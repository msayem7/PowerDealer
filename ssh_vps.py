import paramiko
import sys
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(
        hostname='82.112.235.77',
        username='root',
        password='s-A-yem+19#74',
        timeout=30
    )
    
    print("--- Checking if migrations ran ---")
    stdin, stdout, stderr = client.exec_command('docker exec powerdealer_backend python manage.py showmigrations')
    migrations = ''.join(stdout)
    print(migrations)
    
    print("\n--- Checking full backend logs ---")
    stdin, stdout, stderr = client.exec_command('docker logs powerdealer_backend 2>&1')
    logs = ''.join(stdout)
    print(logs[:3000])
    
    print("\n--- Checking health endpoint ---")
    stdin, stdout, stderr = client.exec_command('curl -s http://localhost:8000/api/health/ || echo "Health check failed"')
    health = ''.join(stdout)
    print(health)
    
    client.close()
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
