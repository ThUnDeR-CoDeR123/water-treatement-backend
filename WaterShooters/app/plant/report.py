import io
from datetime import date
from typing import Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session
from app.models.base import EquipmentLog, ChemicalLog, FlowLog, FlowParameterLog
from sqlalchemy.sql import func
from collections import defaultdict
import io
import csv

def generate_plant_report_csv(db: Session, plant_id: int, start_date: Optional[date], end_date: Optional[date]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    def group_logs_by_date(logs, date_attr="created_at"):
        grouped = defaultdict(list)
        for log in logs:
            log_date = getattr(log, date_attr).date() if hasattr(getattr(log, date_attr), 'date') else getattr(log, date_attr)
            grouped[log_date].append(log)
        return grouped

    # Header
    writer.writerow([f"Plant Report - Plant ID: {plant_id}"])
    writer.writerow([f"Date Range: {start_date} to {end_date}"])
    writer.writerow([])

    # Equipment Logs
    writer.writerow(["Equipment Logs"])
    equipment_logs = db.query(EquipmentLog).filter(
        EquipmentLog.plant_id == plant_id,
        EquipmentLog.del_flag == False,
        func.date(EquipmentLog.created_at).between(start_date, end_date)
    ).all()
    equipment_by_date = group_logs_by_date(equipment_logs)
    writer.writerow(["Date", "Equipment ID", "Status", "Maintenance Done"])
    for log_date in sorted(equipment_by_date):
        for log in equipment_by_date[log_date]:
            writer.writerow([
                log_date,
                log.plant_equipment_id,
                log.equipment_status,
                log.maintenance_done
            ])
    writer.writerow([])

    # Chemical Logs
    writer.writerow(["Chemical Logs"])
    chemical_logs = db.query(ChemicalLog).filter(
        ChemicalLog.plant_id == plant_id,
        ChemicalLog.del_flag == False,
        func.date(ChemicalLog.created_at).between(start_date, end_date)
    ).all()
    chemical_by_date = group_logs_by_date(chemical_logs)
    writer.writerow(["Date", "Chemical ID", "Quantity Used", "Quantity Left", "Sludge Discharge"])
    for log_date in sorted(chemical_by_date):
        for log in chemical_by_date[log_date]:
            writer.writerow([
                log_date,
                log.plant_chemical_id,
                log.quantity_used,
                log.quantity_left,
                log.sludge_discharge
            ])
    writer.writerow([])

    # Flow Logs
    writer.writerow(["Flow Logs"])
    flow_logs = db.query(FlowLog).filter(
        FlowLog.plant_id == plant_id,
        FlowLog.del_flag == False,
        func.date(FlowLog.created_at).between(start_date, end_date)
    ).all()
    flow_by_date = group_logs_by_date(flow_logs)
    writer.writerow(["Date", "Inlet Value", "Outlet Value"])
    for log_date in sorted(flow_by_date):
        for log in flow_by_date[log_date]:
            writer.writerow([
                log_date,
                log.inlet_value,
                log.outlet_value
            ])
    writer.writerow([])

    # Flow Parameter Logs
    writer.writerow(["Flow Parameter Logs"])
    flow_param_logs = db.query(FlowParameterLog).filter(
        FlowParameterLog.plant_id == plant_id,
        FlowParameterLog.del_flag == False,
        func.date(FlowParameterLog.created_at).between(start_date, end_date)
    ).all()
    flow_param_by_date = group_logs_by_date(flow_param_logs)
    writer.writerow(["Date", "Parameter ID", "Inlet Value", "Outlet Value"])
    for log_date in sorted(flow_param_by_date):
        for log in flow_param_by_date[log_date]:
            writer.writerow([
                log_date,
                log.plant_flow_parameter_id,
                log.inlet_value,
                log.outlet_value
            ])
    writer.writerow([])

    return buffer.getvalue().encode("utf-8")


def generate_plant_report_pdf(db: Session, plant_id: int, start_date: Optional[date], end_date: Optional[date]) -> bytes:
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - inch

    def draw_header(title: str):
        nonlocal y
        p.setFont("Helvetica-Bold", 14)
        p.drawString(inch, y, title)
        y -= 20

    def draw_line():
        nonlocal y
        p.setLineWidth(0.5)
        p.line(inch, y, width - inch, y)
        y -= 15

    def draw_text(label: str, value):
        nonlocal y
        p.setFont("Helvetica", 10)
        text = f"{label}: {value}"
        p.drawString(inch, y, text)
        y -= 15
        if y < inch:
            p.showPage()
            y = height - inch

    def group_logs_by_date(logs, date_attr="created_at"):
        grouped = defaultdict(list)
        for log in logs:
            log_date = getattr(log, date_attr).date() if hasattr(getattr(log, date_attr), 'date') else getattr(log, date_attr)
            grouped[log_date].append(log)
        return grouped

    # Header
    draw_header(f"Plant Report - Plant ID: {plant_id}")
    draw_text("Date Range", f"{start_date} to {end_date}")
    draw_line()

    # Equipment Logs
    draw_header("Equipment Logs")
    equipment_logs = db.query(EquipmentLog).filter(
        EquipmentLog.plant_id == plant_id,
        EquipmentLog.del_flag == False,
        func.date(EquipmentLog.created_at).between(start_date, end_date)
    ).all()
    equipment_by_date = group_logs_by_date(equipment_logs)
    for log_date in sorted(equipment_by_date):
        draw_text("Date", log_date)
        for log in equipment_by_date[log_date]:
            draw_text("  Equipment ID", log.plant_equipment_id)
            draw_text("  Status", log.equipment_status)
            draw_text("  Maintenance Done", log.maintenance_done)
            draw_line()

    # Chemical Logs
    draw_header("Chemical Logs")
    chemical_logs = db.query(ChemicalLog).filter(
        ChemicalLog.plant_id == plant_id,
        ChemicalLog.del_flag == False,
        func.date(ChemicalLog.created_at).between(start_date, end_date)
    ).all()
    chemical_by_date = group_logs_by_date(chemical_logs)
    for log_date in sorted(chemical_by_date):
        draw_text("Date", log_date)
        for log in chemical_by_date[log_date]:
            draw_text("  Chemical ID", log.plant_chemical_id)
            draw_text("  Quantity Used", log.quantity_used)
            draw_text("  Quantity Left", log.quantity_left)
            draw_text("  Sludge Discharge", log.sludge_discharge)
            draw_line()

    # Flow Logs
    draw_header("Flow Logs")
    flow_logs = db.query(FlowLog).filter(
        FlowLog.plant_id == plant_id,
        FlowLog.del_flag == False,
        func.date(FlowLog.created_at).between(start_date, end_date)
    ).all()
    flow_by_date = group_logs_by_date(flow_logs)
    for log_date in sorted(flow_by_date):
        draw_text("Date", log_date)
        for log in flow_by_date[log_date]:
            draw_text("  Inlet Value", log.inlet_value)
            draw_text("  Outlet Value", log.outlet_value)
            draw_line()

    # Flow Parameter Logs
    draw_header("Flow Parameter Logs")
    flow_param_logs = db.query(FlowParameterLog).filter(
        FlowParameterLog.plant_id == plant_id,
        FlowParameterLog.del_flag == False,
        func.date(FlowParameterLog.created_at).between(start_date, end_date)
    ).all()
    flow_param_by_date = group_logs_by_date(flow_param_logs)
    for log_date in sorted(flow_param_by_date):
        draw_text("Date", log_date)
        for log in flow_param_by_date[log_date]:
            draw_text("  Parameter ID", log.plant_flow_parameter_id)
            draw_text("  Inlet Value", log.inlet_value)
            draw_text("  Outlet Value", log.outlet_value)
            draw_line()

    # Save PDF
    p.save()
    buffer.seek(0)
    return buffer.read()