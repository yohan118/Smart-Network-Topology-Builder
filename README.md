# Smart-Network-Topology-Builder
A Python tool that takes business requirements as input and automatically designs a complete enterprise network. You describe a company, and it calculates subnets, assigns VLANs, builds security policies, and generates ready-to-use Cisco IOS configuration files for every device.

## What It Is

Designing an enterprise network by hand means doing subnet math for every department, making sure no IP ranges overlap, keeping VLAN IDs consistent across every site, and typing the same Cisco commands again and again for each router and switch. It is slow and easy to get wrong.

This tool does all of that automatically. You give it the requirements once, and it produces a full, consistent design in a few seconds.

You tell it things like:

- How many departments and how many users in each
- How many branch offices (plus the HQ)
- Whether you need a VPN between branches
- Whether you need Guest WiFi
- Whether you need a server room at HQ

And it gives you back:

- A subnet plan with correct, non-overlapping IP ranges for every department
- VLAN assignments following common best practices
- Security policies turned into real Cisco ACL rules
- Cisco IOS config files for each router and switch
- VPN / IPSec config when branches need to be connected
- A topology diagram, a CSV addressing table, and a PDF report

## How It Works

The tool runs in four stages:

### 1. Collect requirements

`input_handler.py` asks the questions and stores the answers as a clean Python data structure. It validates the input along the way (no negative numbers, no empty names, no duplicate department names). In demo mode it loads a built-in sample company instead of asking.

### 2. Run the design engines

The requirements are passed through three engines in order:

- **`engines/subnet_calculator.py`** — uses Python's built-in `ipaddress` library to do the subnet math. It picks the right subnet size for each department based on user count (for example 50 users gets a /26 with 62 usable hosts), aligns each subnet to its correct block boundary so ranges never overlap, and works out the network address, gateway, broadcast address, and first and last usable IP for each one.
- **`engines/vlan_designer.py`** — assigns VLAN IDs following best practice (IT = 10, HR = 20, Finance = 30, Management = 40, Servers = 50, Guest WiFi = 60, native = 99).
- **`engines/security_engine.py`** — turns plain security rules like "Finance is isolated from HR" or "Guest WiFi is isolated from everything" into actual Cisco extended ACL syntax.

### 3. Generate the configs

`engines/config_generator.py` takes all the calculated data and fills in **Jinja2 templates** (`templates/router_template.j2` and `templates/switch_template.j2`). A template is just a Cisco config with blanks in it; the generator pours the real IP addresses, VLAN IDs, and ACL lines into those blanks. This is how the tool produces working configs without anyone typing them by hand.

### 4. Produce the output

The finished design is exported in several formats:

- `output/report_generator.py` writes the **CSV** addressing table and the **PDF** report
- `output/visualizer.py` draws the **text topology diagram**
- the device configs are saved as **.txt** files, one per device
- everything is saved into the `exports/` folder
- `main.py` also prints a clean, colored summary to the terminal using the `rich` library

In one sentence: it collects requirements into a data structure, runs them through the subnet / VLAN / security engines, feeds the results into Jinja2 templates to build the Cisco configs, and exports everything as config files, a CSV, and a PDF.

## How To Use It

### 1. Install the required libraries

```
pip install -r requirements.txt
```

This installs `rich` (terminal output), `reportlab` (PDF report), and `jinja2` (config templates). The `ipaddress` and `csv` libraries are built into Python, so there is nothing to install for those.

### 2. Run it

To run it for real and answer the questions yourself:

```
python main.py
```

To see it work instantly using the built-in sample company:

```
python main.py demo
```

(If `python` is not recognised on your system, use `python3` instead.)

### 3. Find your output

After it runs, all the generated files are in the `exports/` folder:

```
exports/
├── configs/    hq_router_config.txt, hq_switch_config.txt,
│               branch_x_router_config.txt, branch_x_switch_config.txt,
│               acl_rules.txt, vpn_config.txt
├── reports/    ip_addressing_table.csv, network_report.pdf
└── diagrams/   topology_diagram.txt
```

You can open the `.txt` configs and paste them straight into Cisco Packet Tracer or a real device, open the CSV in any spreadsheet program, and view the PDF report.

## Project Structure

```
smart-network-topology-builder/
├── main.py                  entry point, runs everything
├── input_handler.py         user input and validation
├── engines/
│   ├── subnet_calculator.py subnet math
│   ├── vlan_designer.py     VLAN logic
│   ├── security_engine.py   ACL / firewall rules
│   └── config_generator.py  Cisco configs from templates
├── output/
│   ├── visualizer.py        topology diagram
│   └── report_generator.py  PDF + CSV
├── templates/
│   ├── router_template.j2
│   └── switch_template.j2
├── exports/                 generated files appear here
├── requirements.txt
└── README.md
```

## Technologies Used

- **Python 3** — core language
- **ipaddress** (built-in) — all subnet calculations
- **Jinja2** — templates for the Cisco config files
- **rich** — formatted terminal output
- **reportlab** — PDF report generation
- **csv** (built-in) — spreadsheet export
