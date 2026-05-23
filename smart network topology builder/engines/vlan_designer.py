VLAN_MAP = {}
VLAN_MAP["IT"] = 10
VLAN_MAP["HR"] = 20
VLAN_MAP["Finance"] = 30
VLAN_MAP["Management"] = 40
VLAN_MAP["Servers"] = 50
VLAN_MAP["Guest WiFi"] = 60
VLAN_MAP["Guest"] = 60


def assign_vlans(departments):
    result = []
    next_vlan = 70
    used = []
    for dept in departments:
        name = dept["name"]
        if name in VLAN_MAP:
            vlan = VLAN_MAP[name]
        else:
            vlan = next_vlan
            next_vlan = next_vlan + 10
        while vlan in used:
            vlan = next_vlan
            next_vlan = next_vlan + 10
        used.append(vlan)
        item = {}
        item["department"] = name
        item["vlan"] = vlan
        item["port_type"] = "access"
        result.append(item)
    return result


def native_vlan():
    return 99
