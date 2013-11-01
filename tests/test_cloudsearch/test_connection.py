import boto.cloudsearch
from boto.cloudsearch.domain import Domain

from moto import mock_cloudsearch
#from tests.helpers import requires_boto_gte

REGION = 'us-west-1'
DOMAIN = 'test-domain'

@mock_cloudsearch
def test_create_domains():
    conn = boto.cloudsearch.connect_to_region(REGION)
    response = conn.create_domain(DOMAIN)

@mock_cloudsearch
def test_cloudsearch_connect_result_endpoints():
    conn = boto.cloudsearch.connect_to_region(REGION)
    response = conn.create_domain(DOMAIN)
    domain = Domain(conn, response)

    assert domain.doc_service_arn == "arn:aws:cs:%s:1234567890:doc/%s" % (REGION, DOMAIN)
    assert domain.doc_service_endpoint.startswith('doc-%s' % DOMAIN)
    assert domain.doc_service_endpoint.endswith('%s.cloudsearch.amazonaws.com' % REGION)

    assert domain.search_service_arn == "arn:aws:cs:%s:1234567890:search/%s" % (REGION, DOMAIN)
    assert domain.search_service_endpoint.startswith('search-%s' % DOMAIN)
    assert domain.search_service_endpoint.endswith('%s.cloudsearch.amazonaws.com' % REGION)

@mock_cloudsearch
def test_cloudsearch_connect_result_statuses():
    conn = boto.cloudsearch.connect_to_region(REGION)
    response = conn.create_domain(DOMAIN)
    domain = Domain(conn, response)

    assert domain.created is True
    assert domain.processing is False
    assert domain.requires_index_documents is False
    assert domain.deleted is False

@mock_cloudsearch
def test_cloudsearch_connect_result_details():
    conn = boto.cloudsearch.connect_to_region(REGION)
    response = conn.create_domain(DOMAIN)
    domain = Domain(conn, response)

    assert domain.id == '1234567890/%s' % DOMAIN
    assert domain.name == DOMAIN

@mock_cloudsearch
def test_cloudsearch_documentservice_creation():
    conn = boto.cloudsearch.connect_to_region(REGION)
    response = conn.create_domain(DOMAIN)
    domain = Domain(conn, response)

    document = domain.get_document_service()

    assert document.endpoint.startswith('doc-%s' % DOMAIN)
    assert document.endpoint.endswith('%s.cloudsearch.amazonaws.com' % REGION)

@mock_cloudsearch
def test_cloudsearch_searchservice_creation():
    conn = boto.cloudsearch.connect_to_region(REGION)
    response = conn.create_domain(DOMAIN)
    domain = Domain(conn, response)

    search = domain.get_search_service()

    assert search.endpoint.startswith('search-%s' % DOMAIN)
    assert search.endpoint.endswith('%s.cloudsearch.amazonaws.com' % REGION)

@mock_cloudsearch
def test_cloudsearch_deletion():
    conn = boto.cloudsearch.connect_to_region(REGION)
    conn.create_domain(DOMAIN)
    response = conn.delete_domain(DOMAIN)
    # TODO: check response

@mock_cloudsearch
def test_cloudsearch_index_documents_resp():
    conn = boto.cloudsearch.connect_to_region(REGION)
    conn.create_domain(DOMAIN)
    response = conn.index_documents(DOMAIN)


'''@mock_cloudsearch
def test_describe_domains():
    conn = boto.cloudsearch.connect_to_region(REGION)
    domain = Domain(conn, conn.describe_domains([DOMAIN])[0])
    assert domain.domain_name == DOMAIN
    assert domain.search_service_endpoint.startswith('search-%s' % DOMAIN)
    assert domain.search_service_endpoint.endswith('%s.cloudsearch.amazonaws.com' % REGION)
    assert domain.doc_service_endpoint.startswith('doc-%s' % DOMAIN)
    assert domain.doc_service_endpoint.endswith('%s.cloudsearch.amazonaws.com' % REGION)
'''
