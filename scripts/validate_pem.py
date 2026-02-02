import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
p='e:/water-project/backend/safeTap/safeTap/firebase-credentials.json'
creds=json.load(open(p,'r',encoding='utf-8'))
pk=creds['private_key']
# mimic formatting logic
pk2=pk.strip()
if pk2.startswith('"') and pk2.endswith('"'):
    pk2=pk2[1:-1]
pk2=pk2.replace('\\n','\n')
pk2=pk2.replace('-----BEGIN PRIVATE KEY-----','-----BEGIN PRIVATE KEY-----\n')
pem=pk2.encode('utf-8')
print('First80:',pk2[:80])
print('Contains header:', '-----BEGIN PRIVATE KEY-----' in pk2)
try:
    key=serialization.load_pem_private_key(pem,password=None,backend=default_backend())
    print('Loaded key OK:', type(key))
except Exception as e:
    import traceback
    print('Error:', e)
    traceback.print_exc()
