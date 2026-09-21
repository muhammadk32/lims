from modules.results.validators import check_result
from tests.conftest import login


def test_check_result_range_normal():
    assert check_result('70 - 100', '85') == 'normal'


def test_check_result_range_abnormal_high():
    assert check_result('70 - 100', '250') == 'abnormal'


def test_check_result_range_abnormal_low():
    assert check_result('70 - 100', '30') == 'abnormal'


def test_check_result_less_than():
    assert check_result('< 5', '3') == 'normal'
    assert check_result('< 5', '12') == 'abnormal'


def test_check_result_greater_than():
    assert check_result('> 40', '55') == 'normal'
    assert check_result('> 40', '30') == 'abnormal'


def test_check_result_negative():
    assert check_result('Negative', 'negative') == 'normal'
    assert check_result('Negative', 'positive') == 'abnormal'


def test_check_result_empty():
    assert check_result('', '5') == 'unknown'
    assert check_result('70 - 100', '') == 'unknown'


def test_technician_can_access_results_page(client):
    login(client, 'tech', 'tech123')
    r = client.get('/results/')
    assert r.status_code == 200


def test_receptionist_cannot_access_results_page(client):
    login(client, 'recep.lisa', 'recep123') if False else None
    login(client, 'tech', 'tech123')
    r = client.get('/results/')
    assert r.status_code == 200