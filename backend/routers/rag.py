from fastapi import APIRouter, HTTPException

from ..schemas import RAGQuery
from ..services.rag_service import generate_rag_answer


router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)


@router.post("/explain")
def explain_maintenance(request: RAGQuery):

    try:
        result = generate_rag_answer(
            query=request.query,
            model=request.model
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )