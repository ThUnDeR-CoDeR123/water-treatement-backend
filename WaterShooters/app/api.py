from fastapi import FastAPI
from app.user.routes import userRouter
from app.user.forgetPasswordRoutes import forgetRouter
from app.plant.routes import plantrouter
from app.parameter.routes import flowParameterRouter
from app.logs.chemical.routes import chemicalLogRouter
from app.logs.parameter.routes import flowParameterLogRouter 
from app.logs.graph.routes import graphLogRouter
from app.logs.equipment.routes import equipmentLogRouter
from app.equipment.routes import equipmentRouter
from app.chemical.routes import chemicalRouter
from app.logs.flow.images import imageRouter




def register_routes(app: FastAPI):
    app.include_router(userRouter)
    app.include_router(forgetRouter)
    app.include_router(plantrouter)
    app.include_router(flowParameterRouter)
    app.include_router(chemicalLogRouter)
    app.include_router(flowParameterLogRouter)
    app.include_router(graphLogRouter)
    app.include_router(equipmentLogRouter)
    app.include_router(equipmentRouter)
    app.include_router(chemicalRouter)
    app.include_router(imageRouter)