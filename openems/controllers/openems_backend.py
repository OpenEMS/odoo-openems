from odoo import http


class OpenemsBackend(http.Controller):
    @http.route("/openems_backend/info", auth="user", type="json")
    def index(self):
        # Get user
        user_id = http.request.env.context.get("uid")
        res_users = http.request.env["res.users"].sudo()
        user_rec = res_users.search_read(
            [("id", "=", user_id)],
            ["login", "name", "groups_id", "global_role", "openems_language"],
        )[0]
        res_users.browse([user_id])

        # Get res group model
        res_groups_model = http.request.env["res.groups"].sudo()

        # Get Manager and Reader group
        manager_group = res_groups_model.env.ref("openems.group_openems_manager")
        reader_group = res_groups_model.env.ref("openems.group_openems_reader")

        manager_group_id = manager_group["id"]
        reader_group_id = reader_group["id"]

        # Get user attributes
        global_role = user_rec["global_role"]
        if manager_group_id in user_rec["groups_id"]:
            # Manager group
            global_role = "admin"

        # Get specific Device roles
        device_user_role_model = http.request.env["openems.device_user_role"]
        user_role_ids = device_user_role_model.search_read(
            [("user_id", "=", user_id)], ["id", "role"]
        )

        # Get Devices
        device_model = http.request.env["openems.device"]
        devices = device_model.search_read(
            [], ["id", "name", "user_role_ids", "comment", "producttype"]
        )
        devs = []
        for device_rec in devices:
            # Set user role per group
            role = "guest"
            if manager_group_id in user_rec["groups_id"]:
                # Manager group
                role = "admin"
            elif reader_group_id in user_rec["groups_id"]:
                # Reader group
                role = "guest"

            # Set specific user role
            for device_role_id in device_rec["user_role_ids"]:
                for user_role_id in user_role_ids:
                    if device_role_id == user_role_id["id"]:
                        role = user_role_id["role"]

            # Prepare result
            devs.append(
                {
                    "id": device_rec["id"],
                    "name": device_rec["name"],
                    "comment": device_rec["comment"],
                    "producttype": device_rec["producttype"],
                    "role": role,
                }
            )

        return {
            "user": {
                "id": user_rec["id"],
                "login": user_rec["login"],
                "name": user_rec["name"],
                "global_role": global_role,
                "language": user_rec["openems_language"],
            },
            "devices": devs,
        }
