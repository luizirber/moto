import re
import sure  # noqa

import moto.server as server

'''
Test the different server responses
'''


def test_ec2_server_get():
    backend = server.create_backend_app("ec2")
    test_client = backend.test_client()

    res = test_client.get('/?Action=RunInstances&ImageId=ami-60a54009')

    groups = re.search("<instanceId>(.*)</instanceId>", res.data)
    instance_id = groups.groups()[0]

    res = test_client.get('/?Action=DescribeInstances')
    res.data.should.contain(instance_id)
