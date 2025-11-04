from fastapi import APIRouter, UploadFile, Form
from research.services.ai_summary_service import analyze_document
from research.services.db_service import save_research_summary

router = APIRouter()

@router.post("/upload")
async def upload_research_file(
    client_name: str = Form(...),
    file: UploadFile = None
):
    contents = await file.read()
    summary = await analyze_document(contents.decode("utf-8"))
    record = save_research_summary(client_name, summary)
    return {"client": client_name, "summary": summary, "record_id": record.id}
