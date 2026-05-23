import os
from jinja2 import Environment, FileSystemLoader
from engines.security_engine import wildcard


def setup_env():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder = os.path.join(here, "templates")
    env = Environment(loader=FileSystemLoader(folder))
    return env


def clean_name(name):
    return name.replace(" ", "_").upper()


def build_vlan_data(subnets, vlans, wan_links):
    combined = []
    port = 1
    for s in subnets:
        vlan_id = 0
        for v in vlans:
            if v["department"] == s["department"]:
                vlan_id = v["vlan"]
        item = {}
        item["department"] = s["department"]
        item["department_clean"] = clean_name(s["department"])
        item["vlan"] = vlan_id
        item["network"] = s["network"]
        item["mask"] = s["mask"]
        item["gateway"] = s["gateway"]
        item["wildcard"] = wildcard(s["prefix"])
        item["start_port"] = port
        item["end_port"] = port + 9
        combined.append(item)
        port = port + 10

    links = []
    for l in wan_links:
        net = l["subnet"].split("/")[0]
        copy = {}
        copy["name"] = l["name"]
        copy["network"] = net
        copy["hq_ip"] = l["hq_ip"]
        copy["branch_ip"] = l["branch_ip"]
        links.append(copy)
    return combined, links


def generate_router(env, hostname, vlan_data, wan_links, acl, has_vpn):
    template = env.get_template("router_template.j2")
    text = template.render(hostname=hostname, vlans=vlan_data, wan_links=wan_links, acl=acl, has_vpn=has_vpn)
    return text


def generate_switch(env, hostname, vlan_data):
    template = env.get_template("switch_template.j2")
    text = template.render(hostname=hostname, vlans=vlan_data)
    return text


def make_vpn_config(wan_links):
    lines = []
    lines.append("VPN / IPSec Configuration Summary")
    lines.append("=================================")
    for l in wan_links:
        lines.append("")
        lines.append(l["name"])
        lines.append(" HQ peer: " + l["hq_ip"])
        lines.append(" Branch peer: " + l["branch_ip"])
        lines.append(" Encryption: AES")
        lines.append(" Auth: pre-share key vpnkey123")
    return "\n".join(lines)
