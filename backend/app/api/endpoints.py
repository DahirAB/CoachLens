from fastapi import APIRouter, HTTPException
from ..models.schemas import GeneratePlanRequest, GeneratePlanResponse
from ..optimiser.engine import TrainingPlanOptimiser, InfeasiblePlanError

router = APIRouter()

@router.post("/generate-plan", response_model=GeneratePlanResponse)
async def generate_plan(request: GeneratePlanRequest):
    try:
        optimiser = TrainingPlanOptimiser(request)
        plan = optimiser.solve()
        return plan
    except InfeasiblePlanError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

