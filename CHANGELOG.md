Change Log
----------
2.0.9

Fix unit test and flake8 issues.

2.0.8

Enhancement - parse callout as preconditions for XmindZen.
Auto determine rule v1 or v2 by checking descendants of the 3rd level nodes(which is v1 testcase level) have priority marker or not.  

2.0.7

Bug fix - convert execution type to 1 by default.

2.0.6

Support XmindZen file type, since comments feature is removed in xmind zen, so we cannot create `preconditions` from XmindZen.

2.0.5

Bug fix - failed to parse priority maker, thanks @nancy301513.

2.0.4

Bug fix - failed to parse comment node.

2.0.3

Bug fix - root suite should not have a title.

2.0.1

Bug fix - web app should not cache the connector.
Bug fix - combination title parts incorrectly under some conditions.

2.0.0

Upgrade to v2.0, support convert more flexible xmind files.

1.1.7

Keep line breaks and html tag for text fields, such as test suite summary, test case steps.

1.1.4

Fix potential failure if test action node is empty.

1.1.1

Fix potential failure if the node is a image.

1.1.0

Handle unicode in xmind.

1.0.0

The baby version.