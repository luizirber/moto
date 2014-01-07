import sure  # noqa

import moto.server as server

'''
Test the different server responses
'''


def test_sts_get_session_token():
    backend = server.create_backend_app("sts")
    test_client = backend.test_client()

    res = test_client.get('/?Action=GetSessionToken')
    res.status_code.should.equal(200)
    res.data.should.contain("SessionToken")
    res.data.should.contain("AccessKeyId")
