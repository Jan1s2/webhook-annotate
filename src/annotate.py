import re
from flask import Flask, request, abort
import json
import base64

app = Flask(__name__)

@app.route('/mutate', methods=['POST'])
def mutate():
    admission_review = request.get_json()

    try:
        resource = admission_review['request']['object']
        kind = resource['kind']
        spec = resource.get('spec', {})
        annotations = resource.get('metadata', {}).get('annotations', {})
    except KeyError:
        abort(400, 'Invalid admission review')

    match kind:
        case 'Ingress':
            mutate_ingress(spec, annotations)

    admission_review['response'] = {
        'uid': admission_review['request']['uid'],
        'allowed': True,
        'patchType': 'JSONPatch',
        'patch': base64.b64encode(json.dumps([
            {"op": "replace", "path": "/spec", "value": spec},
            {"op": "replace", "path": "/metadata/annotations", "value": annotations}
        ]).encode()).decode()
    }

    return admission_review

def mutate_ingress(spec, annotations):
    rules = spec.get('rules', [])
    if annotations.get('kubernetes.io/tls-acme', "true") == 'false':
        return
    annotations['kubernetes.io/tls-acme'] = 'true'
    annotations['ingress.kubernetes.io/ssl-redirect'] = 'false'
    annotations['acme.cert-manager.io/http01-edit-in-place'] = 'true'
    spec['tls'] = []

    for rule in rules:
        if not rule.get('http'):
            continue
        host = rule['host']
        spec.tls.append({
            'hosts': [host],
            'secretName': f'{host}-tls'
        })


def main():
    app.run(host='0.0.0.0', port=4433, ssl_context=('/etc/sslcerts/cert.pem', '/etc/sslcerts/key.pem'))

if __name__ == '__main__':
    main()
