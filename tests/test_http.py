import requests

r = requests.get('http://127.0.0.1:5000', allow_redirects=True)
print(f'Status: {r.status_code}')
print(f'URL: {r.url}')
print(f'Has login form: {"login" in r.text.lower()}')
print(f'Has Pertamina: {"Pertamina" in r.text}')
print(f'Has KKP: {"KKP" in r.text}')
print(f'Has username field: {"username" in r.text}')
print(f'Has password field: {"password" in r.text}')
print(f'Page length: {len(r.text)} chars')
