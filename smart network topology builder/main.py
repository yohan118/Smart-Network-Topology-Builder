import os
import sys
import time

from input_handler import get_requirements, sample_requirements
from engines.subnet_calculator import make_subnets, make_wan_links
from engines.vlan_designer import assign_vlans
from engines.security_engine import make_policies, make_acl_lines
from engines import config_generator
from output.visualizer import build_diagram
from output.report_generator import write_csv, write_pdf

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def build_department_list(data):
    departments = []
    for d in data["departments"]:
        departments.append({"name": d["name"], "users": d["users"]})
    if data["servers"] == "yes":
        departments.append({"name": "Servers", "users": 10})
    if data["guest"] == "yes":
        departments.append({"name": "Guest WiFi", "users": 30})
    return departments


def location_base(index):
    return "192.168." + str(index + 1) + ".0/24"


def run():
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        data = sample_requirements()
    else:
        data = get_requirements()

    start = time.time()

    departments = build_department_list(data)
    branch_count = data["branches"]
    total_branches = branch_count + 1

    locations = ["HQ"]
    b = 1
    while b <= branch_count:
        locations.append("Branch " + str(b))
        b = b + 1

    vlans = assign_vlans(departments)

    subnets_by_location = {}
    all_subnets_flat = []
    loc_index = 0
    while loc_index < len(locations):
        loc = locations[loc_index]
        try:
            subnets = make_subnets(departments, location_base(loc_index))
        except ValueError as e:
            console.print("\n[bold red]DESIGN ERROR[/bold red]")
            console.print("  " + str(e))
            console.print("  Tip: one /24 per location holds about 254 addresses total.")
            return
        for s in subnets:
            for v in vlans:
                if v["department"] == s["department"]:
                    s["vlan"] = v["vlan"]
            flat = dict(s)
            flat["location"] = loc
            all_subnets_flat.append(flat)
        subnets_by_location[loc] = subnets
        loc_index = loc_index + 1

    wan_links = make_wan_links(branch_count)
    policies = make_policies(departments, data["vpn"], branch_count)
    acl_lines = make_acl_lines(subnets_by_location["HQ"])

    total_users = 0
    for d in data["departments"]:
        total_users = total_users + d["users"]

    here = os.path.dirname(os.path.abspath(__file__))
    configs_dir = os.path.join(here, "exports", "configs")
    reports_dir = os.path.join(here, "exports", "reports")
    diagrams_dir = os.path.join(here, "exports", "diagrams")

    env = config_generator.setup_env()
    has_vpn = data["vpn"] == "yes"

    files_made = []

    loc_index = 0
    while loc_index < len(locations):
        loc = locations[loc_index]
        vlan_data, links_data = config_generator.build_vlan_data(subnets_by_location[loc], vlans, wan_links)
        if loc == "HQ":
            router_text = config_generator.generate_router(env, "HQ_Router", vlan_data, links_data, acl_lines, has_vpn)
            fname = "hq_router_config.txt"
        else:
            router_text = config_generator.generate_router(env, loc.replace(" ", "_") + "_Router", vlan_data, [], [], has_vpn)
            fname = loc.lower().replace(" ", "_") + "_router_config.txt"
        save(os.path.join(configs_dir, fname), router_text)
        files_made.append(fname)

        switch_text = config_generator.generate_switch(env, loc.replace(" ", "_") + "_Switch", vlan_data)
        sw_fname = loc.lower().replace(" ", "_") + "_switch_config.txt"
        save(os.path.join(configs_dir, sw_fname), switch_text)
        files_made.append(sw_fname)
        loc_index = loc_index + 1

    save(os.path.join(configs_dir, "acl_rules.txt"), "\n".join(acl_lines))
    files_made.append("acl_rules.txt")

    if has_vpn:
        vpn_text = config_generator.make_vpn_config(wan_links)
        save(os.path.join(configs_dir, "vpn_config.txt"), vpn_text)
        files_made.append("vpn_config.txt")

    csv_path = os.path.join(reports_dir, "ip_addressing_table.csv")
    write_csv(csv_path, all_subnets_flat)
    files_made.append("ip_addressing_table.csv")

    diagram = build_diagram(data["company"], locations, subnets_by_location, wan_links)
    diagram_path = os.path.join(diagrams_dir, "topology_diagram.txt")
    save(diagram_path, diagram)
    files_made.append("topology_diagram.txt")

    pdf_path = os.path.join(reports_dir, "network_report.pdf")
    write_pdf(pdf_path, data["company"], total_users, total_branches, all_subnets_flat, policies, diagram, files_made)
    files_made.append("network_report.pdf")

    elapsed = round(time.time() - start, 2)
    show_output(data, locations, total_users, elapsed, all_subnets_flat, policies, diagram, files_made)


def save(path, text):
    f = open(path, "w")
    f.write(text)
    f.close()


def show_output(data, locations, total_users, elapsed, all_subnets, policies, diagram, files_made):
    header = "[bold cyan]SMART NETWORK TOPOLOGY BUILDER[/bold cyan]\n"
    header = header + "Company: " + data["company"] + "\n"
    header = header + "Branches: " + str(len(locations)) + "\n"
    header = header + "Total Users: " + str(total_users) + "\n"
    header = header + "Design Time: " + str(elapsed) + " seconds"
    console.print(Panel(header, expand=False))

    table = Table(title="Subnet Design")
    table.add_column("Location")
    table.add_column("Department")
    table.add_column("Subnet")
    table.add_column("VLAN")
    table.add_column("Gateway")
    table.add_column("Hosts")
    for row in all_subnets:
        table.add_row(row["location"], row["department"], row["subnet"], str(row["vlan"]), row["gateway"], str(row["available"]))
    console.print(table)

    console.print("\n[bold green]SECURITY DESIGN[/bold green]")
    for p in policies:
        console.print("  [green]+[/green] " + p)

    console.print("\n[bold yellow]TOPOLOGY SUMMARY[/bold yellow]")
    console.print(diagram)

    console.print("\n[bold magenta]FILES GENERATED[/bold magenta]")
    for fname in files_made:
        console.print("  [magenta]+[/magenta] " + fname)


if __name__ == "__main__":
    run()
