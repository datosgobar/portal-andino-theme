import nose.tools

import ckan.tests.helpers as helpers
import ckan.tests.factories as factories
import ckan.logic as logic
import ckan.model as model


assert_equals = nose.tools.assert_equals
assert_raises = nose.tools.assert_raises
eq = nose.tools.eq_
ok = nose.tools.ok_
raises = nose.tools.raises


class TestDelete:
    def setup(self):
        helpers.reset_db()

    def test_delete_group_purges_group(self):
        sysadmin = factories.Sysadmin()
        group = factories.Group(user=sysadmin)

        helpers.call_action('group_delete', id=group['name'])

        assert_raises(logic.NotFound, helpers.call_action, 'group_show',
                      context={}, id=group['name'])