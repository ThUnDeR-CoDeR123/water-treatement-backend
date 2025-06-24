import io
from datetime import date
from typing import Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session
from app.models.base import EquipmentLog, ChemicalLog, FlowLog, FlowParameterLog
from sqlalchemy.sql import func


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
    for log in equipment_logs:
        draw_text("Equipment ID", log.plant_equipment_id)
        draw_text("Status", log.equipment_status)
        draw_text("Maintenance Done", log.maintenance_done)
        draw_text("Date", log.created_at)
        draw_line()

    # Chemical Logs
    draw_header("Chemical Logs")
    chemical_logs = db.query(ChemicalLog).filter(
        ChemicalLog.plant_id == plant_id,
        ChemicalLog.del_flag == False,
        func.date(ChemicalLog.created_at).between(start_date, end_date)
    ).all()
    for log in chemical_logs:
        draw_text("Chemical ID", log.plant_chemical_id)
        draw_text("Quantity Used", log.quantity_used)
        draw_text("Quantity Left", log.quantity_left)
        draw_text("Sludge Discharge", log.sludge_discharge)
        draw_text("Date", log.created_at)
        draw_line()

    # Flow Logs
    draw_header("Flow Logs")
    flow_logs = db.query(FlowLog).filter(
        FlowLog.plant_id == plant_id,
        FlowLog.del_flag == False,
        func.date(FlowLog.created_at).between(start_date, end_date)
    ).all()
    for log in flow_logs:
        draw_text("Inlet Value", log.inlet_value)
        draw_text("Outlet Value", log.outlet_value)
        draw_text("Date", log.created_at)
        draw_line()

    # Flow Parameter Logs
    draw_header("Flow Parameter Logs")
    flow_param_logs = db.query(FlowParameterLog).filter(
        FlowParameterLog.plant_id == plant_id,
        FlowParameterLog.del_flag == False,
        func.date(FlowParameterLog.created_at).between(start_date, end_date)
    ).all()
    for log in flow_param_logs:
        draw_text("Parameter ID", log.plant_flow_parameter_id)
        draw_text("Inlet Value", log.inlet_value)
        draw_text("Outlet Value", log.outlet_value)
        draw_text("Date", log.created_at)
        draw_line()

    # Save PDF
    p.save()
    buffer.seek(0)
    return buffer.read()
