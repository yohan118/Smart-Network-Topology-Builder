def make_policies(departments, has_vpn, branch_count):
    names = []
    for dept in departments:
        names.append(dept["name"])

    rules = []

    if "Finance" in names:
        rules.append("Finance VLAN isolated from HR VLAN")
        rules.append("Finance VLAN isolated from Guest WiFi")
    if "Management" in names:
        rules.append("Management VLAN has full access")
    if "Guest WiFi" in names or "Guest" in names:
        rules.append("Guest WiFi isolated from all internal VLANs")
    if "Servers" in names and "IT" in names:
        rules.append("Servers only accessible from IT VLAN")
    if "HR" in names and "Finance" in names:
        rules.append("HR has no access to Finance")

    if has_vpn == "yes":
        i = 1
        while i <= branch_count:
            rules.append("VPN tunnel: HQ to Branch " + str(i))
            i = i + 1

    return rules


def make_acl_lines(subnets):
    lines = []
    lines.append("ip access-list extended SECURITY_POLICY")

    finance = None
    hr = None
    guest = None
    servers = None
    it = None

    for s in subnets:
        if s["department"] == "Finance":
            finance = s
        if s["department"] == "HR":
            hr = s
        if s["department"] == "Guest WiFi" or s["department"] == "Guest":
            guest = s
        if s["department"] == "Servers":
            servers = s
        if s["department"] == "IT":
            it = s

    if finance is not None and hr is not None:
        wild = wildcard(finance["prefix"])
        lines.append(" deny ip " + hr["network"] + " " + wildcard(hr["prefix"]) + " " + finance["network"] + " " + wild)

    if guest is not None:
        wild = wildcard(guest["prefix"])
        lines.append(" deny ip " + guest["network"] + " " + wild + " 192.168.0.0 0.0.255.255")

    if servers is not None and it is not None:
        lines.append(" permit ip " + it["network"] + " " + wildcard(it["prefix"]) + " " + servers["network"] + " " + wildcard(servers["prefix"]))
        lines.append(" deny ip any " + servers["network"] + " " + wildcard(servers["prefix"]))

    lines.append(" permit ip any any")
    return lines


def wildcard(prefix):
    bits = 32 - prefix
    total = (2 ** bits) - 1
    octets = []
    octets.append((total >> 24) & 255)
    octets.append((total >> 16) & 255)
    octets.append((total >> 8) & 255)
    octets.append(total & 255)
    out = ""
    i = 0
    while i < 4:
        out = out + str(octets[i])
        if i < 3:
            out = out + "."
        i = i + 1
    return out
