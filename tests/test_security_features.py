import pytest

from app import app, security


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    security.captchas.clear()
    with app.test_client() as client:
        # Ensure a clean session for each test
        with client.session_transaction() as session:
            session.clear()
        yield client


def get_csrf_token(client):
    response = client.get('/api/security/status')
    assert response.status_code == 200
    data = response.get_json()
    token = data.get('csrf_token')
    assert token
    return token, data


def solve_captcha(question):
    if ' + ' in question:
        a, b = question.split(' + ')
        return int(a) + int(b)
    if ' - ' in question:
        a, b = question.split(' - ')
        return int(a) - int(b)
    if ' × ' in question:
        a, b = question.split(' × ')
        return int(a) * int(b)
    raise ValueError(f'Unknown CAPTCHA format: {question}')


def test_security_status_exposes_expected_fields(client):
    token, status = get_csrf_token(client)
    assert status['captcha_enabled'] is True
    assert 'rate_limit_threshold' in status
    assert 'rate_limited' in status
    assert token == status['csrf_token']


def test_feedback_requires_authentication(client):
    token, _ = get_csrf_token(client)
    response = client.post(
        '/api/feedback',
        json={'identification_id': 1, 'feedback': 'correct'},
        headers={'X-CSRF-Token': token}
    )
    assert response.status_code == 401


def test_captcha_flow_enforces_verification(client):
    token, _ = get_csrf_token(client)

    # Request a new CAPTCHA challenge
    captcha_response = client.post(
        '/api/security/captcha',
        headers={'X-CSRF-Token': token}
    )
    assert captcha_response.status_code == 200
    captcha_payload = captcha_response.get_json()
    assert 'captcha_id' in captcha_payload
    assert 'question' in captcha_payload

    # Submit an incorrect answer first
    wrong_response = client.post(
        '/api/security/verify',
        json={
            'captcha_id': captcha_payload['captcha_id'],
            'answer': '999'
        },
        headers={'X-CSRF-Token': get_csrf_token(client)[0]}
    )
    assert wrong_response.status_code in (400, 429)
    wrong_payload = wrong_response.get_json()
    assert wrong_payload['success'] is False
    assert wrong_payload['code'] in {'incorrect_answer', 'too_many_attempts'}

    # Submit the correct answer
    correct_answer = solve_captcha(captcha_payload['question'])
    success_response = client.post(
        '/api/security/verify',
        json={
            'captcha_id': captcha_payload['captcha_id'],
            'answer': str(correct_answer)
        },
        headers={'X-CSRF-Token': get_csrf_token(client)[0]}
    )
    assert success_response.status_code == 200
    success_payload = success_response.get_json()
    assert success_payload['success'] is True
    assert success_payload['status']['is_trusted'] is True
