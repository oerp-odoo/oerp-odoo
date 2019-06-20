from . import common


class TestComputeMethods(common.TestMachineCommon):
    """Class to test compute methods for machine models."""

    @classmethod
    def setUpClass(cls):
        """Set up records for name_get test."""
        super(TestComputeMethods, cls).setUpClass()
        cls.MachineDbsInstance = cls.env['machine.dbs.instance']
        cls.dbs_instance_1 = cls.MachineDbsInstance.create({
            'name': 'Cluster 1',
            'machine_instance_id': cls.mit_1_1.id,
            'dbs_id': cls.db_postgresql_960.id,
            'port': 5434,
        })

    def test_01_compute_db_instance_amounts(self):
        """Test DB Users/Databases amount as is by default."""
        self.assertEqual(self.dbs_instance_1.users_count, 0)
        self.assertEqual(self.dbs_instance_1.databases_count, 0)
        self.assertEqual(self.mit_1_1.os_users_count, 0)

    def test_02_compute_db_instance_amounts(self):
        """Test DB Users/Databases/OS Users amount by modifying it.

        Case 1: specify amount directly on field.
        Case 2: Add related records to compute amount from it.
        Case 3: Remove related records to recompute amount from from
            entered value.
        """
        # Case 1.
        self.dbs_instance_1._users_count = 10
        self.dbs_instance_1._databases_count = 5
        self.mit_1_1._os_users_count = 3
        self.assertEqual(self.dbs_instance_1.users_count, 10)
        self.assertEqual(self.dbs_instance_1.databases_count, 5)
        self.assertEqual(self.mit_1_1.os_users_count, 3)
        # Case 2.
        self.dbs_instance_1.write({
            'dbs_instance_user_ids': [(0, 0, {'username': 'U1'})],
            'dbs_instance_db_ids': [(0, 0, {'name': 'D1'})],
        })
        self.mit_1_1.os_user_ids = [(0, 0, {'username': 'OS_U1'})]
        self.assertEqual(self.dbs_instance_1.users_count, 1)
        self.assertEqual(self.dbs_instance_1.databases_count, 1)
        self.assertEqual(self.mit_1_1.os_users_count, 1)
        # Case 3.
        self.dbs_instance_1.dbs_instance_user_ids.unlink()
        self.dbs_instance_1.dbs_instance_db_ids.unlink()
        self.mit_1_1.os_user_ids.unlink()
        self.assertEqual(self.dbs_instance_1.users_count, 10)
        self.assertEqual(self.dbs_instance_1.databases_count, 5)
        self.assertEqual(self.mit_1_1.os_users_count, 3)
