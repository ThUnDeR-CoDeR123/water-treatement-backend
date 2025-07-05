from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.logs.chemical.crud import *
from app.logs.chemical.schema import ( 
    ChemicalLogSchema
)
from app.database import get_db
from app.auth.jwt import get_current_user,getPriviledgeUser,getAdmin
from app.models.base import User

chemicalLogRouter = APIRouter(prefix="/api/v1/logs", tags=["chemicalLog"])




@chemicalLogRouter.post("/create/chemical")
def create_log(
    log: ChemicalLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(getPriviledgeUser)
):
    try:
        print(log)
        return createChemicalLog(db, log,current_user.user_id)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))


@chemicalLogRouter.post("/chemical")
def get_chemical_logs(
    log: ChemicalLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return getChemicalLogs(db, log, current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@chemicalLogRouter.put("/update/chemical", response_model=ChemicalLogSchema)
def update_chemical_logs(
    log: ChemicalLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return updateChemicalLogs(db, log, current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@chemicalLogRouter.delete("/delete/chemical/{chemical_log_id}")
def delete_chemical_logs(
    chemical_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(getAdmin)
):
    try:
        deleteChemicalLog(db, ChemicalLogSchema(chemical_log_id=chemical_log_id))
        return {"message": "Chemical log deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

