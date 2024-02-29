def migrate(cr, version):
    cr.execute("""
               SELECT device_id, user_id, time_to_wait, last_notification
               INTO fems_alerting_migrate
               FROM fems_device_user_role
               WHERE time_to_wait > 0;
               """)
