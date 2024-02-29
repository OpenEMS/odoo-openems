from odoo.api import Environment, SUPERUSER_ID

def migrate(cr, version):
    cr.execute("""
               INSERT INTO fems_alerting (device_id, device_name, user_id, user_login, offline_delay, warning_delay, fault_delay, offline_last_notification)
               SELECT device_id, dev.name, user_id, usr.login, time_to_wait, 0, 0, last_notification
               FROM fems_alerting_migrate AS migrate
               LEFT JOIN fems_device AS dev ON dev.id = migrate.device_id
               LEFT JOIN res_users AS usr ON usr.id = migrate.user_id
               """)
    cr.execute('DROP TABLE fems_alerting_migrate')
