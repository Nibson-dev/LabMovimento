from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Importando os 4 modelos
from explainlab_engine.physics_models.vertical_motion import VerticalMotion
from explainlab_engine.physics_models.inclined_plane import InclinedPlane
from explainlab_engine.physics_models.projectile_motion import ProjectileMotion
from explainlab_engine.physics_models.horizontal_mruv import HorizontalMRUV

app = FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"],
)

class SimulationRequest(BaseModel):
    model_type: str
    parameters: dict

# Registrando os 4 modelos no dicionário
models = {
    "vertical_motion": VerticalMotion(),
    "inclined_plane": InclinedPlane(),
    "projectile_motion": ProjectileMotion(),
    "horizontal_mruv": HorizontalMRUV()
}

@app.post("/api/simulate")
async def simulate(request: SimulationRequest):
    if request.model_type not in models:
        raise HTTPException(status_code=400, detail="Modelo físico não encontrado.")
    
    model = models[request.model_type]
    
    try:
        result = model.solve(**request.parameters)
        return result
    except Exception as e:
        # Log do erro no terminal para facilitar debugging
        print(f"Erro na simulação: {e}")
        raise HTTPException(status_code=500, detail=str(e))