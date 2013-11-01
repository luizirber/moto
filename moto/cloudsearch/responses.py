import json
from urlparse import parse_qs, urlparse

from jinja2 import Template

from moto.core.responses import BaseResponse
from .models import cloudsearch_backend


class CloudSearchResponse(BaseResponse):

    def _get_param(self, param_name):
        return self.querystring.get(param_name, [None])[0]

    def _get_int_param(self, param_name):
        value = self._get_param(param_name)
        if value is not None:
            return int(value)

    def _get_multi_param(self, param_prefix):
        return [value[0] for key, value in self.querystring.items() if key.startswith(param_prefix)]

    def create_domain(self):
        domain_name = self._get_param('DomainName')
        region = self.headers['host'].split('.')[1]
        cloudsearch_backend.add_domain(domain_name)

        template = Template(CREATE_DOMAIN_TEMPLATE)
        return template.render(domain=domain_name, region=region)

    def delete_domain(self):
        domain_name = self._get_param('DomainName')
        region = self.headers['host'].split('.')[1]
        cloudsearch_backend.delete_domain(domain_name)

        template = Template(DELETE_DOMAIN_TEMPLATE)
        return template.render(domain=domain_name, region=region)

    def describe_domains(self):
        domain_names = self._get_multi_param('DomainNames')
        region = self.headers['host'].split('.')[1]
        template = Template(DESCRIBE_DOMAINS_TEMPLATE)
        return template.render(domains=domain_names, region=region)

    def index_documents(self):
        domain_name = self._get_param('DomainName')
        region = self.headers['host'].split('.')[1]
        members = cloudsearch_backend.index_documents(domain_name)

        template = Template(INDEX_DOCUMENTS_TEMPLATE)
        return template.render(domain=domain_name, members=members)

    def documents_batch_response(self, request, full_url, headers):
        if hasattr(request, 'body'):
            # Boto
            self.body = request.body
        else:
            # Flask server
            self.body = request.data

        querystring = parse_qs(urlparse(full_url).query)
        if not querystring:
            querystring = parse_qs(self.body)
        if not querystring:
            querystring = headers

        self.uri = full_url
        self.path = urlparse(full_url).path
        self.querystring = querystring
        self.method = request.method

        self.header = dict(request.headers)
        self.response_headers = headers

        if self.method == 'POST':
            # TODO:
            #   check sdf size < 5 MB
            #   check sdf len  < 1000 items
            #   only checking json request, check xml too
            response = json.dumps(cloudsearch_backend.batch(json.loads(self.body)))
        else:
            raise NotImplementedError("Method {0} is not implemented in CloudSearch documents batch".format(self.method))

        if isinstance(response, basestring):
            return 200, headers, response
        else:
            status_code, headers, response_content = response
            return status_code, headers, response_content


    def search_response(self, request, full_url, headers):
        if hasattr(request, 'body'):
            # Boto
            self.body = request.body
        else:
            # Flask server
            self.body = request.data

        querystring = parse_qs(urlparse(full_url).query)
        if not querystring:
            querystring = parse_qs(self.body)
        if not querystring:
            querystring = headers

        self.uri = full_url
        self.path = urlparse(full_url).path
        self.querystring = querystring
        self.method = request.method

        self.header = dict(request.headers)
        self.response_headers = headers

        if self.method == 'GET':
            # TODO:
            response = json.dumps(cloudsearch_backend.search(querystring))
        else:
            raise NotImplementedError("Method {0} has not been implemented in the CloudSearch documents batch".format(method))

        if isinstance(response, basestring):
            return 200, headers, response
        else:
            status_code, headers, response_content = response
            return status_code, headers, response_content


DESCRIBE_DOMAINS_TEMPLATE = """<DescribeDomainsResponse xmlns="http://cloudsearch.amazonaws.com/doc/2011-02-01">
  <DescribeDomainsResult>
    <DomainStatusList>
      {% for domain in domains %}
      <member>
        <SearchPartitionCount>1</SearchPartitionCount>
        <SearchService>
          <Arn>arn:aws:cs:{{region}}:1234567890:search/{{domain}}</Arn>
          <Endpoint>search-{{domain}}-zl2syfqt56dgygqk2a3gismj6q.{{region}}.cloudsearch.amazonaws.com</Endpoint>
        </SearchService>
        <NumSearchableDocs>200658</NumSearchableDocs>
        <SearchInstanceType>search.m1.small</SearchInstanceType>
        <Created>true</Created>
        <DomainId>160241911954/site</DomainId>
        <Processing>false</Processing>
        <SearchInstanceCount>1</SearchInstanceCount>
        <DomainName>{{domain}}</DomainName>
        <RequiresIndexDocuments>false</RequiresIndexDocuments>
        <Deleted>false</Deleted>
        <DocService>
          <Arn>arn:aws:cs:us-east-1:160241911954:doc/site</Arn>
          <Endpoint>doc-{{domain}}-zl2syfqt56dgygqk2a3gismj6q.{{region}}.cloudsearch.amazonaws.com</Endpoint>
        </DocService>
      </member>
      {% endfor %}
    </DomainStatusList>
  </DescribeDomainsResult>
  <ResponseMetadata>
    <RequestId>6b2d5751-bf09-11e1-9cbb-03417d143e55</RequestId>
  </ResponseMetadata>
</DescribeDomainsResponse>
"""

CREATE_DOMAIN_TEMPLATE = '''
<CreateDomainResponse xmlns="http://cloudsearch.amazonaws.com/doc/2011-02-01">
  <CreateDomainResult>
    <DomainStatus>
      <SearchPartitionCount>0</SearchPartitionCount>
      <SearchService>
        <Arn>arn:aws:cs:{{region}}:1234567890:search/{{domain}}</Arn>
        <Endpoint>search-{{domain}}-userdomain.{{region}}.cloudsearch.amazonaws.com</Endpoint>
      </SearchService>
      <NumSearchableDocs>0</NumSearchableDocs>
      <Created>true</Created>
      <DomainId>1234567890/{{domain}}</DomainId>
      <Processing>false</Processing>
      <SearchInstanceCount>0</SearchInstanceCount>
      <DomainName>{{domain}}</DomainName>
      <RequiresIndexDocuments>false</RequiresIndexDocuments>
      <Deleted>false</Deleted>
      <DocService>
        <Arn>arn:aws:cs:{{region}}:1234567890:doc/{{domain}}</Arn>
        <Endpoint>doc-{{domain}}-userdomain.{{region}}.cloudsearch.amazonaws.com</Endpoint>
      </DocService>
    </DomainStatus>
  </CreateDomainResult>
  <ResponseMetadata>
    <RequestId>00000000-0000-0000-0000-000000000000</RequestId>
  </ResponseMetadata>
</CreateDomainResponse>
'''

DELETE_DOMAIN_TEMPLATE = '''
<DeleteDomainResponse xmlns="http://cloudsearch.amazonaws.com/doc/2011-02-01">
  <DeleteDomainResult>
    <DomainStatus>
      <SearchPartitionCount>0</SearchPartitionCount>
      <SearchService>
        <Arn>arn:aws:cs:{{region}}:1234567890:search/{{domain}}</Arn>
        <Endpoint>search-{{domain}}-userdomain.{{region}}.cloudsearch.amazonaws.com</Endpoint>
      </SearchService>
      <NumSearchableDocs>0</NumSearchableDocs>
      <Created>true</Created>
      <DomainId>1234567890/demo</DomainId>
      <Processing>false</Processing>
      <SearchInstanceCount>0</SearchInstanceCount>
      <DomainName>{{domain}}</DomainName>
      <RequiresIndexDocuments>false</RequiresIndexDocuments>
      <Deleted>false</Deleted>
      <DocService>
        <Arn>arn:aws:cs:{{region}}:1234567890:doc/{{domain}}</Arn>
        <Endpoint>doc-{{domain}}-userdomain.{{region}}.cloudsearch.amazonaws.com</Endpoint>
      </DocService>
    </DomainStatus>
  </DeleteDomainResult>
  <ResponseMetadata>
    <RequestId>00000000-0000-0000-0000-000000000000</RequestId>
  </ResponseMetadata>
</DeleteDomainResponse>
'''

INDEX_DOCUMENTS_TEMPLATE = '''
<IndexDocumentsResponse xmlns="http://cloudsearch.amazonaws.com/doc/2011-02-01">
  <IndexDocumentsResult>
    <FieldNames>
      {% for member in members %}
      <member>{{member}}</member>
      {% endfor %}
    </FieldNames>
  </IndexDocumentsResult>
  <ResponseMetadata>
    <RequestId>eb2b2390-6bbd-11e2-ab66-93f3a90dcf2a</RequestId>
  </ResponseMetadata>
</IndexDocumentsResponse>
'''
