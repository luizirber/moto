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

    def describe_domains(self):
        domain_names = self._get_multi_param('DomainNames')

        template = Template(DESCRIBE_DOMAINS_TEMPLATE)
        return template.render(domains=domain_names)

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
          <Arn>arn:aws:cs:us-east-1:160241911954:search/site</Arn>
          <Endpoint>search-site-zl2syfqt56dgygqk2a3gismj6q.us-east-1.cloudsearch.amazonaws.com</Endpoint>
        </SearchService>
        <NumSearchableDocs>200658</NumSearchableDocs>
        <SearchInstanceType>search.m1.small</SearchInstanceType>
        <Created>true</Created>
        <DomainId>160241911954/site</DomainId>
        <Processing>false</Processing>
        <SearchInstanceCount>1</SearchInstanceCount>
        <DomainName>site</DomainName>
        <RequiresIndexDocuments>false</RequiresIndexDocuments>
        <Deleted>false</Deleted>
        <DocService>
          <Arn>arn:aws:cs:us-east-1:160241911954:doc/site</Arn>
          <Endpoint>doc-site-zl2syfqt56dgygqk2a3gismj6q.us-east-1.cloudsearch.amazonaws.com</Endpoint>
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
