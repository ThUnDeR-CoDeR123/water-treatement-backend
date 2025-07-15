
from fastapi import FastAPI
from app.logs.equipment.schedular.database import  get_db
import threading
from contextlib import asynccontextmanager
import time
from datetime import datetime,timezone,timedelta
from app.logs.equipment.crud import *

def check_time_and_run():
    print("Checking time to run scheduled task...",get_IST())
    # Get current time in IST
    ist_time = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
    # Check if current time is 22:00 (with a 1-minute window to avoid missing)
    if ist_time.hour == 22:
        print("It's 10 PM IST, running scheduled task...")
        try:
            add_equipment_log()
        except Exception as e:
            print(f"Error while adding equipment log: {str(e)}")

def run_scheduler():
    while True:
        check_time_and_run()
        time.sleep(1500)  # Check every minute to reduce CPU usage

def start_scheduler():
    """Starts the scheduler in a background thread."""
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("Scheduler started successfully!")

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()  # Start the scheduler thread
    yield  # App runs while the scheduler is running
    print("Scheduler stopped.")

#
def add_equipment_log():
    """
    This function adds equipment log everyday at 10pm if no equipment log is there for that particular equipment
    """
    with next(get_db()) as db:  # Use the context manager to get a session
        
        #fetch all the plant equipments
        plant_equipment_list = db.query(PlantEquipment).filter(PlantEquipment.del_flag == False).all()
        for plant_equipment in plant_equipment_list:
            # Check if there is any log for the same date and same shift
            existing_log = db.query(EquipmentLog).filter(
                EquipmentLog.plant_equipment_id == plant_equipment.plant_equipment_id,
                EquipmentLog.del_flag == False,
                EquipmentLog.created_at >= time.strftime("%Y-%m-%d 00:00:00"),
                EquipmentLog.created_at <= time.strftime("%Y-%m-%d 23:59:59")
            ).first()
            if not existing_log:
                # If no log exists, create a new equipment log entry
                print(f"Adding new equipment log for plant equipment ID: {plant_equipment.plant_equipment_id}")
                createEquipmentLog(
                    db=db,
                    log=EquipmentLogSchema(
                        plant_id=plant_equipment.plant_id,
                        shift=2,  # Assuming the shift is "Night" for this example
                        equipment_status=0,
                        plant_equipment_id=plant_equipment.plant_equipment_id,
                        equipment_remark="Ok",
                        maintenance_done=False
                    ),
                    user_id=1  # Assuming user_id 1 is the admin or system user who creates these logs
                )
