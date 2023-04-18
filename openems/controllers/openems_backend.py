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

        # return empty device (use pagination) list if user is manager or reader
        if manager_group_id in user_rec["groups_id"] or reader_group_id in user_rec["groups_id"]:
            return {
                "user": {
                    "id": user_rec["id"],
                    "login": user_rec["login"],
                    "name": user_rec["name"],
                    "global_role": global_role,
                    "language": user_rec["openems_language"],
                },
                "devices": [],
            }

        # Get specific Device roles
        device_user_role_model = http.request.env["openems.device_user_role"]
        user_role_ids = device_user_role_model.search_read(
            [("user_id", "=", user_id)], ["id", "role"]
        )

        # Get Devices
        device_model = http.request.env["openems.device"]
        devices = device_model.search_read(
            [], ["id", "name", "user_role_ids", "comment", "producttype",
                 "lastmessage", "first_setup_protocol_date"]
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
            dev = {
                "id": device_rec["id"],
                "name": device_rec["name"],
                "comment": device_rec["comment"],
                "producttype": device_rec["producttype"],
                "role": role,
                "lastmessage": device_rec["lastmessage"],
            }

            if device_rec["first_setup_protocol_date"]:
                dev["first_setup_protocol_date"] = device_rec[
                    "first_setup_protocol_date"
                ]

            devs.append(dev)

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

    @http.route("/openems_backend/get_edge_with_role", auth="user", type="json")
    def get_edge_with_role(self, edge_id: str):
        user_id = http.request.env.context.get("uid")
        res_users = http.request.env["res.users"].sudo()
        user_rec = res_users.search_read(
            [("id", "=", user_id)],
            ["login", "name", "groups_id"],
        )[0]

        # Get res group model
        res_groups_model = http.request.env["res.groups"].sudo()

        # Get Manager and Reader group
        manager_group = res_groups_model.env.ref("openems.group_openems_manager")
        reader_group = res_groups_model.env.ref("openems.group_openems_reader")

        manager_group_id = manager_group["id"]
        reader_group_id = reader_group["id"]

        # get devices for which the user has permissions
        device_model = http.request.env["openems.device"]
        devices = device_model.search_read(
            [("name", "=", edge_id)],
            ["id", "name", "comment", "producttype", "lastmessage", "first_setup_protocol_date"])

        if len(devices) != 1:
            return {}

        device = devices[0]

        # Get specific Device roles
        device_user_role_model = http.request.env["openems.device_user_role"]
        device_user_roles = device_user_role_model.search_read(
            [("user_id", "=", user_id), ("device_id", "=", device["id"])], ["id", "role"]
        )

        # Set user role per group
        role = "guest"
        if manager_group_id in user_rec["groups_id"]:
            # Manager group
            role = "admin"
        elif reader_group_id in user_rec["groups_id"]:
            # Reader group
            role = "guest"

        # Set specific user role
        if len(device_user_roles) > 0:
            role = device_user_roles[0]["role"]

        dev = {
            "id": device["id"],
            "name": device["name"],
            "comment": device["comment"],
            "producttype": device["producttype"],
            "role": role,
            "lastmessage": device["lastmessage"],
        }
        if device["first_setup_protocol_date"]:
            dev["first_setup_protocol_date"] = device["first_setup_protocol_date"]

        return dev

    @http.route("/openems_backend/get_edges", auth="user", type="json")
    def get_edges(self, limit, page, query=None):
        # Get user
        user_id = http.request.env.context.get("uid")
        res_users = http.request.env["res.users"].sudo()
        user_rec = res_users.search_read(
            [("id", "=", user_id)],
            ["login", "name", "groups_id", "global_role"],
        )[0]

        # Get res group model
        res_groups_model = http.request.env["res.groups"].sudo()

        # Get Manager and Reader group
        manager_group = res_groups_model.env.ref("openems.group_openems_manager")
        reader_group = res_groups_model.env.ref("openems.group_openems_reader")

        manager_group_id = manager_group["id"]
        reader_group_id = reader_group["id"]

        # Get specific Device roles
        device_user_role_model = http.request.env["openems.device_user_role"]
        user_role_ids = device_user_role_model.search_read(
            [("user_id", "=", user_id)], ["id", "role"]
        )

        domain = []
        if query:
            domain = ["|", "|",
                      ("name", "ilike", query),
                      ("comment", "ilike", query),
                      ("producttype", "ilike", query)
                      ]

        # Get Devices
        device_model = http.request.env["openems.device"]
        devices = device_model.search_read(
            domain,
            ["id", "name", "user_role_ids", "comment", "producttype",
                "lastmessage", "first_setup_protocol_date"],
            limit=limit, offset=(page * limit)
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
            dev = {
                "id": device_rec["id"],
                "name": device_rec["name"],
                "comment": device_rec["comment"],
                "producttype": device_rec["producttype"],
                "role": role,
                "lastmessage": device_rec["lastmessage"],
            }

            if device_rec["first_setup_protocol_date"]:
                dev["first_setup_protocol_date"] = device_rec[
                    "first_setup_protocol_date"
                ]

            devs.append(dev)

        return {
            "devices": devs,
        }
