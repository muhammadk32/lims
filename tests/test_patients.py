from tests.conftest import login, logout


def test_login_page_loads(client):
    r = client.get('/login')
    assert r.status_code == 200
    # Page renders brand "LIMS" + "User Login" heading
    assert (
        b'LIMS' in r.data
        or b'Laboratory Management System' in r.data
        or b'User Login' in r.data
        or b'LOGIN' in r.data
    )


def test_login_wrong_password(client):
    r = login(client, 'admin', 'wrongpass')
    assert b'Invalid username or password' in r.data


def test_login_success(client):
    r = login(client, 'admin', 'admin123')
    assert r.status_code == 200
    assert b'Welcome back' in r.data or b'Dashboard' in r.data


def test_logout(client):
    login(client, 'admin', 'admin123')
    r = logout(client)
    assert b'logged out' in r.data.lower() or r.status_code == 200


def test_protected_route_redirects(client):
    r = client.get('/', follow_redirects=False)
    assert r.status_code == 302
    assert '/login' in r.headers.get('Location', '')


def test_health_check(client):
    r = client.get('/healthz')
    assert r.status_code == 200
    data = r.get_json()
    assert data['status'] == 'ok'
    assert data['db'] == 'ok'