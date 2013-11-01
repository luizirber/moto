import uuid

from moto.core import BaseBackend


class CloudSearchBackend(BaseBackend):

    def __init__(self):
        super(CloudSearchBackend, self).__init__()
        self.domains = {}
        self.documents = {}

    def _parse_query(self, query):
        term = query['bq'][0].split("'")[1]
        filters = self._parse_bq(query['bq'][0])
        return term, filters

    def _parse_bq(self, text):
        text = text.strip()

        if text.count('(') == 0:
            cond_type, field, value = text.split()
            if cond_type == 'filter':
                value = int(value)
            elif cond_type == 'field':
                value = value.strip("'")
            return cond_type, field, value

        close_posn = text.rfind(')')
        conds = []
        for posn in range(1, close_posn):
            if text[posn] == '(':
                cond_start = posn + 1
            elif text[posn] == ')':
                new_cond = self._parse_bq(text[cond_start:posn])
                conds.append(new_cond)

        return conds

    def _match_cond(self, cond, field, value, doc):
        if cond == 'field':
            if value.endswith('*') and doc[field].startswith(value.rstrip('*')):
                return True
            elif doc[field] == value:
                return True
        elif cond == 'filter':
            # TODO implement comparisons
            if doc[field] == value:
                return True
        return False

    def add_domain(self, domain_name):
        self.domains[domain_name] = {}

    def delete_domain(self, domain_name):
        self.domains.pop(domain_name)

    def index_documents(self, domain_name):
        domain = self.domains[domain_name]
        return ['member']

    def batch(self, sdf):
        adds = 0
        deletes = 0
        for doc in sdf:
            if doc['type'] == 'add':
                # TODO: do all checks
                self.documents[doc['id']] = doc
                adds += 1
            elif doc['type'] == 'delete':
                # TODO: do all checks
                self.documents.pop(doc['id'])
                deletes += 1
            else:
                # invalid type, what cloudsearch do in this case?
                pass

        return {
            'status': 'success',
            'adds': adds,
            'deletes': deletes,
        }

    def search(self, query):
        results = []
        term, filters = self._parse_query(query)

        for doc_id, doc_values in self.documents.items():
            if all(self._match_cond(cond, field, value, doc_values['fields']) for cond, field, value in filters):
                terms = term.split()
                if len(terms) > 1:
                    if any(t in doc_values['fields']['text'] for t in terms):
                        results.append({'id': doc_id, 'data': doc_values['fields']})
                elif term == "*":
                    results.append({'id': doc_id, 'data': doc_values['fields']})
                else:
                    if "*" in term:
                        term = term.rstrip('*')
                    if term in doc_values['fields']['text']:
                        results.append({'id': doc_id, 'data': doc_values['fields']})

        return {
          'rank': "-text_relevance",
          'match-expr': "(label '%s')" % term,
          'hits': {
            'start': 0,
            'found': len(results),
            'hit': results,
          },
          'info': {
            'rid': uuid.uuid4().hex,
            'time-ms': 2,
            'cpu-time-ms': 0
          }
        }

cloudsearch_backend = CloudSearchBackend()
