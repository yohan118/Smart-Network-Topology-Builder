import ipaddress


def pick_prefix(users):
    needed = users + 2
    prefix = 32
    while prefix > 0:
        size = 2 ** (32 - prefix)
        if size >= needed:
            return prefix
        prefix = prefix - 1
    return 24


def make_subnets(departments, base_network):
    base = ipaddress.ip_network(base_network)
    current = int(base.network_address)
    limit = int(base.broadcast_address)
    results = []
    for dept in departments:
        name = dept["name"]
        users = dept["users"]
        prefix = pick_prefix(users)
        block = 2 ** (32 - prefix)
        if current % block != 0:
            current = current + (block - (current % block))
        if current + block - 1 > limit:
            raise ValueError("Department '" + name + "' (" + str(users) + " users) does not fit in " + base_network + ". Try fewer users or split the department.")
        net = ipaddress.ip_network((current, prefix), strict=False)
        hosts = list(net.hosts())
        first_ip = str(hosts[0])
        last_ip = str(hosts[-1])
        gateway = first_ip
        info = {}
        info["department"] = name
        info["users"] = users
        info["network"] = str(net.network_address)
        info["prefix"] = prefix
        info["subnet"] = str(net.network_address) + "/" + str(prefix)
        info["mask"] = str(net.netmask)
        info["broadcast"] = str(net.broadcast_address)
        info["gateway"] = gateway
        info["first_ip"] = first_ip
        info["last_ip"] = last_ip
        info["available"] = net.num_addresses - 2
        results.append(info)
        current = current + net.num_addresses
    return results


def make_wan_links(branch_count):
    base = ipaddress.ip_network("10.0.0.0/30")
    current = int(base.network_address)
    links = []
    i = 1
    while i <= branch_count:
        net = ipaddress.ip_network((current, 30), strict=False)
        hosts = list(net.hosts())
        link = {}
        link["name"] = "WAN Link to Branch " + str(i)
        link["subnet"] = str(net.network_address) + "/30"
        link["hq_ip"] = str(hosts[0])
        link["branch_ip"] = str(hosts[1])
        links.append(link)
        current = current + 4
        i = i + 1
    return links
