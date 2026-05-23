def build_diagram(company, branches, subnets_by_location, wan_links):
    lines = []
    lines.append("=========================================")
    lines.append(" NETWORK TOPOLOGY - " + company)
    lines.append("=========================================")
    lines.append("")

    locations = list(subnets_by_location.keys())

    hq = locations[0]
    lines.append("[" + hq + " Router] (192.168.1.1)")
    lines.append("    |")
    lines.append("[" + hq + " Core Switch]")
    hq_subnets = subnets_by_location[hq]
    i = 0
    while i < len(hq_subnets):
        s = hq_subnets[i]
        branch = "+--"
        if i == len(hq_subnets) - 1:
            branch = "+--"
        line = "  " + branch + " VLAN " + str(s["vlan"]) + " - " + s["department"]
        line = pad(line, 38) + s["subnet"]
        lines.append(line)
        i = i + 1

    lines.append("")
    for l in wan_links:
        lines.append("  " + l["name"] + "  (" + l["subnet"] + ")")
        lines.append("      HQ " + l["hq_ip"] + " <-----> Branch " + l["branch_ip"])

    lines.append("")

    j = 1
    while j < len(locations):
        loc = locations[j]
        lines.append("-----------------------------------------")
        lines.append("[" + loc + " Router]")
        lines.append("    |")
        lines.append("[" + loc + " Switch]")
        loc_subnets = subnets_by_location[loc]
        k = 0
        while k < len(loc_subnets):
            s = loc_subnets[k]
            line = "  +-- VLAN " + str(s["vlan"]) + " - " + s["department"]
            line = pad(line, 38) + s["subnet"]
            lines.append(line)
            k = k + 1
        lines.append("")
        j = j + 1

    return "\n".join(lines)


def pad(text, width):
    while len(text) < width:
        text = text + " "
    return text
