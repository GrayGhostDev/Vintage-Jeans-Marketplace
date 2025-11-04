from research.db.session import get_session
from research.models.research_model import ResearchSummary

def save_research_summary(client_name: str, summary: str):
    with get_session() as session:
        record = ResearchSummary(client_name=client_name, summary=summary)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record
