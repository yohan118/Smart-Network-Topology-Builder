import csv
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet


def write_csv(path, all_subnets):
    f = open(path, "w", newline="")
    writer = csv.writer(f)
    writer.writerow(["Location", "Department", "VLAN", "Subnet", "Mask", "Gateway", "First IP", "Last IP", "Broadcast", "Hosts"])
    for row in all_subnets:
        writer.writerow([row["location"], row["department"], row["vlan"], row["subnet"], row["mask"], row["gateway"], row["first_ip"], row["last_ip"], row["broadcast"], row["available"]])
    f.close()


def write_pdf(path, company, total_users, branch_count, all_subnets, policies, diagram_text, files_list):
    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Smart Network Topology Report", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Company: " + company, styles["Normal"]))
    story.append(Paragraph("Total Users: " + str(total_users), styles["Normal"]))
    story.append(Paragraph("Branches: " + str(branch_count), styles["Normal"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph("IP Addressing Table", styles["Heading2"]))
    story.append(Spacer(1, 8))

    data = [["Location", "Department", "VLAN", "Subnet", "Gateway", "Hosts"]]
    for row in all_subnets:
        data.append([row["location"], row["department"], str(row["vlan"]), row["subnet"], row["gateway"], str(row["available"])])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#ecf0f1")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("Security Policies", styles["Heading2"]))
    story.append(Spacer(1, 8))
    for p in policies:
        story.append(Paragraph("- " + p, styles["Normal"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Generated Files", styles["Heading2"]))
    story.append(Spacer(1, 8))
    for fname in files_list:
        story.append(Paragraph("- " + fname, styles["Normal"]))

    doc.build(story)
