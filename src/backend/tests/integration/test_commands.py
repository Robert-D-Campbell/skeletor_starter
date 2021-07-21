from django.core.management import call_command
from django.db.utils import OperationalError

from unittest.mock import patch
from tests.utils import CkcAPITestCase, CkcAPIClient

class CommandTests(CkcAPITestCase):

    # Retreive db connection and check if OperationalError is raised
    def test_db_is_ready(self):
        """Test db has started and is available"""
        # Override the behavior of the connection handler and make it return True
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 1)
    # remove timeout from OperationalError
    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """Test waiting for db"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # raise Operational Error 5 times, then return True
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            # check that operationalerror is called 6 times.
            self.assertEqual(gi.call_count, 6)