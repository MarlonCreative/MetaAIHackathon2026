"""One bounded Meta Responses API connectivity check; persist metadata only."""
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from local_config import meta_key
from secure_http import tls_context

ENDPOINT = 'https://api.meta.ai/v1/responses'
MODEL = 'muse-spark-1.3'
REPORT = Path(__file__).resolve().parent.parent / 'reports' / 'meta_live_verification.json'


def verify():
    key = meta_key()
    if not key:
        raise RuntimeError('MODEL_API_KEY is not configured in the ignored local .env')
    payload = {'model': MODEL, 'input': 'Reply with exactly CASAOS_OK.',
               'store': False, 'max_output_tokens': 128}
    request = urllib.request.Request(
        ENDPOINT, data=json.dumps(payload).encode(), method='POST',
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    audit = {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
             'endpoint': ENDPOINT, 'model': MODEL,
             'request_limit': 1, 'max_output_tokens': 128, 'timeout_seconds': 20,
             'provider_storage_requested': False}
    try:
        with urllib.request.urlopen(request, timeout=20, context=tls_context()) as response:
            result = json.load(response)
            audit['http_status'] = response.status
        audit['response_status'] = result.get('status')
        audit['response_id'] = result.get('id')
        audit['usage'] = {k: v for k, v in result.get('usage', {}).items()
                          if k in ('input_tokens', 'output_tokens', 'total_tokens') and type(v) is int}
        audit['output_types'] = [item.get('type') for item in result.get('output', [])]
        audit['expected_reply_observed'] = any(
            part.get('text', '').strip() == 'CASAOS_OK'
            for item in result.get('output', []) if item.get('type') == 'message'
            for part in item.get('content', []) if part.get('type') == 'output_text')
    except urllib.error.HTTPError as exc:
        audit['http_status'] = exc.code
        audit['response_status'] = 'http_error'
        try:
            error = json.load(exc).get('error', {})
            if isinstance(error, dict):
                for field in ('type', 'code'):
                    value = error.get(field)
                    if isinstance(value, str) and len(value) <= 80:
                        audit['provider_error_' + field] = value
        except (ValueError, OSError):
            pass
    except Exception as exc:
        audit['response_status'] = 'request_error'
        audit['error_type'] = type(exc).__name__
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps(audit, indent=2) + '\n')
    print(f"Meta verification: {audit['response_status']}; HTTP {audit.get('http_status', 'unavailable')}; metadata: {REPORT}")
    return audit


if __name__ == '__main__':
    result = verify()
    raise SystemExit(0 if result.get('response_status') == 'completed' else 1)
