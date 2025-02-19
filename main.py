import socketio
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, joinedload
from casbin import Enforcer
from pydantic import BaseModel, conlist

# -------------------------
# Database setup and models
# -------------------------
DATABASE_URL = "postgresql://user:password@db:5432/incident_management"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    source = Column(String)
    host = Column(String)
    state = Column(Integer)
    wikilink = Column(String)
    status = Column(String, default="new")
    created_at = Column(DateTime, default=datetime.utcnow)
    # Link to a MainAlert
    main_alert_id = Column(Integer, ForeignKey('main_alerts.id'), nullable=True)
    main_alert = relationship("MainAlert", back_populates="alerts")

class MainAlert(Base):
    __tablename__ = 'main_alerts'
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, index=True)
    source = Column(String)
    host = Column(String)
    state = Column(Integer)
    wikilink = Column(String)
    counter = Column(Integer, default=0)
    last_linked_time = Column(DateTime, default=datetime.utcnow)
    # Each main alert belongs to an Incident
    incident_id = Column(Integer, ForeignKey('incidents.id'), nullable=True)
    alerts = relationship("Alert", back_populates="main_alert")
    incident = relationship("Incident", back_populates="main_alerts")

class IncidentComment(Base):
    __tablename__ = 'incident_comments'
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey('incidents.id'))
    login_name = Column(String)
    comment_text = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    incident = relationship("Incident", back_populates="comments")

class Incident(Base):
    __tablename__ = 'incidents'
    id = Column(Integer, primary_key=True, index=True)
    incident_name = Column(String, index=True)
    status = Column(String, default="open")  # "open", "resolved", or "discarded"
    team = Column(String, default="team1")
    assignee = Column(String, default="person1")
    severity = Column(String, default="MEDIUM")
    wikilink = Column(String, nullable=True)
    source = Column(String, nullable=True)
    host = Column(String, nullable=True)
    state = Column(Integer, nullable=True)
    first_alert_time = Column(DateTime, default=datetime.utcnow)
    last_alert_time = Column(DateTime, nullable=True)
    last_resolved_time = Column(DateTime, nullable=True)
    first_resolved_time = Column(DateTime, nullable=True)
    reopened_time = Column(DateTime, nullable=True)
    alert_count = Column(Integer, default=0)
    reopen_count = Column(Integer, default=0)
    merged = Column(Boolean, default=False)
    definitively_resolved = Column(Boolean, default=False)
    main_alerts = relationship("MainAlert", back_populates="incident", cascade="all, delete-orphan")
    comments = relationship("IncidentComment", back_populates="incident", cascade="all, delete-orphan")

# -------------------------
# Casbin and FastAPI setup
# -------------------------
casbin_enforcer = Enforcer("/app/rbac_model.conf", "/app/rbac_policy.csv")
app = FastAPI()
origins = ["http://localhost:5000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=origins)
socket_app = socketio.ASGIApp(sio, other_asgi_app=app, socketio_path="/socket.io")

# -------------------------
# Pydantic Schemas
# -------------------------
class AlertCreate(BaseModel):
    message: str
    source: str
    host: str
    wikilink: str
    state: int

class IncidentRename(BaseModel):
    new_name: str

class LinkMainAlertPayload(BaseModel):
    main_alert_id: int

class IncidentUpdateSeverity(BaseModel):
    severity: str

class IncidentUpdateTeam(BaseModel):
    team: str

class IncidentCommentCreate(BaseModel):
    login_name: str
    comment_text: str

class IncidentCommentUpdate(BaseModel):
    comment_text: str

class BulkLinkMainAlertsPayload(BaseModel):
    main_alert_ids: conlist(int, min_length=1)

class IncidentUpdateAssignee(BaseModel):
    assignee: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------
# Startup event
# -------------------------
@app.on_event("startup")
def on_startup():
    import time
    from sqlalchemy.exc import OperationalError
    retries = 10
    for i in range(retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            break
        except OperationalError:
            print(f"Database not ready (attempt {i+1}/{retries}). Retrying in 3s...")
            time.sleep(3)
    else:
        raise Exception("Could not connect to the database after multiple retries.")
    Base.metadata.create_all(bind=engine)

# -------------------------
# Endpoints
# -------------------------
@app.post("/alerts/")
async def create_alert(alert: AlertCreate, db: SessionLocal = Depends(get_db)):
    now = datetime.utcnow()
    db_alert = Alert(
        message=alert.message,
        source=alert.source,
        host=alert.host,
        state=alert.state,
        wikilink=alert.wikilink
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)

    existing_main_alert = (
        db.query(MainAlert)
        .join(Incident, isouter=True)
        .filter(
            MainAlert.message == alert.message,
            MainAlert.source == alert.source,
            MainAlert.host == alert.host,
            MainAlert.wikilink == alert.wikilink,
            MainAlert.state == alert.state,
            ((Incident.id.is_(None)) | (Incident.definitively_resolved == False))
        )
        .first()
    )

    if existing_main_alert:
        existing_main_alert.counter += 1
        existing_main_alert.last_linked_time = now
        db_alert.main_alert_id = existing_main_alert.id
        db.commit()
        db.refresh(existing_main_alert)
        db.refresh(db_alert)

        if existing_main_alert.incident_id:
            incident = db.query(Incident).filter(Incident.id == existing_main_alert.incident_id).first()
            if incident:
                if incident.status == "resolved" and not incident.definitively_resolved:
                    incident.status = "open"
                    incident.reopened_time = now
                    incident.reopen_count += 1
                incident.alert_count += 1
                incident.last_alert_time = now
                db.commit()
                db.refresh(incident)
                await sio.emit("incident_update", {"type": "create", "incident_id": incident.id})
                return {
                    "alert": db_alert,
                    "main_alert": {
                        "id": existing_main_alert.id,
                        "message": existing_main_alert.message,
                        "counter": existing_main_alert.counter,
                        "last_linked_time": existing_main_alert.last_linked_time,
                    },
                    "incident": incident,
                }
            else:
                new_incident = Incident(
                    incident_name=alert.message,
                    status="open",
                    alert_count=1,
                    severity="MEDIUM",
                    wikilink=alert.wikilink,
                    source=alert.source,
                    host=alert.host,
                    state=alert.state,
                    first_alert_time=now,
                    last_alert_time=now,
                )
                db.add(new_incident)
                db.commit()
                db.refresh(new_incident)
                existing_main_alert.incident_id = new_incident.id
                db.commit()
                db.refresh(existing_main_alert)
                await sio.emit("incident_update", {"type": "create", "incident_id": new_incident.id})
                return {
                    "alert": db_alert,
                    "main_alert": {
                        "id": existing_main_alert.id,
                        "message": existing_main_alert.message,
                        "counter": existing_main_alert.counter,
                        "last_linked_time": existing_main_alert.last_linked_time,
                    },
                    "incident": new_incident,
                }
        else:
            new_incident = Incident(
                incident_name=alert.message,
                status="open",
                alert_count=1,
                severity="MEDIUM",
                wikilink=alert.wikilink,
                source=alert.source,
                host=alert.host,
                state=alert.state,
                first_alert_time=now,
                last_alert_time=now,
            )
            db.add(new_incident)
            db.commit()
            db.refresh(new_incident)
            existing_main_alert.incident_id = new_incident.id
            db.commit()
            db.refresh(existing_main_alert)
            await sio.emit("incident_update", {"type": "create", "incident_id": new_incident.id})
            return {
                "alert": db_alert,
                "main_alert": {
                    "id": existing_main_alert.id,
                    "message": existing_main_alert.message,
                    "counter": existing_main_alert.counter,
                    "last_linked_time": existing_main_alert.last_linked_time,
                },
                "incident": new_incident,
            }
    else:
        new_main_alert = MainAlert(
            message=alert.message,
            source=alert.source,
            host=alert.host,
            state=alert.state,
            wikilink=alert.wikilink,
            counter=1,
            last_linked_time=now,
        )
        db.add(new_main_alert)
        db.commit()
        db.refresh(new_main_alert)

        db_alert.main_alert_id = new_main_alert.id
        db.commit()
        db.refresh(db_alert)

        new_incident = Incident(
            incident_name=alert.message,
            status="open",
            alert_count=1,
            severity="MEDIUM",
            wikilink=alert.wikilink,
            source=alert.source,
            host=alert.host,
            state=alert.state,
            first_alert_time=now,
            last_alert_time=now,
        )
        db.add(new_incident)
        db.commit()
        db.refresh(new_incident)

        new_main_alert.incident_id = new_incident.id
        db.commit()
        db.refresh(new_main_alert)
        await sio.emit("incident_update", {"type": "create", "incident_id": new_incident.id})
        return {
            "alert": db_alert,
            "main_alert": {
                "id": new_main_alert.id,
                "message": new_main_alert.message,
                "counter": new_main_alert.counter,
                "last_linked_time": new_main_alert.last_linked_time,
            },
            "incident": new_incident,
        }

@app.post("/incidents/{incident_id}/link_main_alert")
async def link_main_alert(incident_id: int, payload: LinkMainAlertPayload, db: SessionLocal = Depends(get_db)):
    target_incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not target_incident:
        raise HTTPException(status_code=404, detail="Target incident not found")
    if target_incident.status == "discarded":
        raise HTTPException(status_code=400, detail="Cannot link a main alert to a discarded incident.")

    main_alert = db.query(MainAlert).filter(MainAlert.id == payload.main_alert_id).first()
    if not main_alert:
        raise HTTPException(status_code=404, detail="Main alert not found")

    if main_alert.incident_id == target_incident.id:
        return {"message": "Main alert already linked to this incident", "incident": target_incident}

    now = datetime.utcnow()
    old_incident = None
    if main_alert.incident_id:
        old_incident = db.query(Incident).filter(Incident.id == main_alert.incident_id).first()

    if old_incident and old_incident.definitively_resolved:
        raise HTTPException(status_code=400, detail="Cannot move main alert from a definitively resolved incident")

    main_alert.incident_id = target_incident.id
    target_incident.alert_count += main_alert.counter
    target_incident.last_alert_time = now
    db.commit()
    db.refresh(main_alert)
    db.refresh(target_incident)

    if old_incident and old_incident.id != target_incident.id:
        db.refresh(old_incident)
        remaining = db.query(MainAlert).filter(MainAlert.incident_id == old_incident.id).count()
        if remaining == 0 and not old_incident.definitively_resolved:
            for comment in old_incident.comments:
                new_comment = IncidentComment(
                    incident_id=target_incident.id,
                    login_name=comment.login_name,
                    comment_text=comment.comment_text
                )
                db.add(new_comment)
            old_incident.status = "discarded"
            db.commit()
            db.refresh(old_incident)
    await sio.emit("incident_update", {"type": "link_main_alert", "incident_id": target_incident.id})
    return {"message": "Main alert linked to target incident", "incident": target_incident}

@app.post("/incidents/{target_incident_id}/drag_link_main_alert/{main_alert_id}")
async def drag_link_main_alert(target_incident_id: int, main_alert_id: int, db: SessionLocal = Depends(get_db)):
    target_incident = db.query(Incident).filter(Incident.id == target_incident_id).first()
    if not target_incident:
        raise HTTPException(status_code=404, detail="Target incident not found")
    if target_incident.status == "discarded":
        raise HTTPException(status_code=400, detail="Cannot link main alerts to a discarded incident")

    main_alert = db.query(MainAlert).filter(MainAlert.id == main_alert_id).first()
    if not main_alert:
        raise HTTPException(status_code=404, detail="Main alert not found")
    if main_alert.incident_id == target_incident.id:
        return {"message": "Main alert already linked to this incident", "incident": target_incident}

    now = datetime.utcnow()
    old_incident = None
    if main_alert.incident_id:
        old_incident = db.query(Incident).filter(Incident.id == main_alert.incident_id).first()
    if old_incident and old_incident.definitively_resolved:
        raise HTTPException(status_code=400, detail="Cannot move main alert from a definitively resolved incident")

    if old_incident:
        old_incident.alert_count -= main_alert.counter
    target_incident.alert_count += main_alert.counter
    target_incident.last_alert_time = now
    main_alert.incident_id = target_incident.id
    db.commit()
    db.refresh(main_alert)
    db.refresh(target_incident)
    if old_incident:
        db.refresh(old_incident)
        remaining_alerts = db.query(MainAlert).filter(MainAlert.incident_id == old_incident.id).count()
        if remaining_alerts == 0:
            old_incident.status = "discarded"
            db.commit()
            db.refresh(old_incident)
    await sio.emit("incident_update", {"type": "drag_link_main_alert", "incident_id": target_incident.id})
    return {"message": "Main alert transferred", "incident": target_incident}

@app.post("/incidents/{source_incident_id}/undo_drag_link_main_alert/{main_alert_id}")
async def undo_drag_link_main_alert(source_incident_id: int, main_alert_id: int, db: SessionLocal = Depends(get_db)):
    source_incident = db.query(Incident).filter(Incident.id == source_incident_id).first()
    if not source_incident:
        raise HTTPException(status_code=404, detail="Source incident not found")
    main_alert = db.query(MainAlert).filter(MainAlert.id == main_alert_id).first()
    if not main_alert:
        raise HTTPException(status_code=404, detail="Main alert not found")
    target_incident = db.query(Incident).filter(Incident.id == main_alert.incident_id).first()
    if not target_incident:
        raise HTTPException(status_code=404, detail="Target incident not found")
    main_alert.incident_id = source_incident.id
    target_incident.alert_count -= main_alert.counter
    source_incident.alert_count += main_alert.counter
    if source_incident.status in ("discarded", "resolved"):
        source_incident.status = "open"
    db.commit()
    db.refresh(source_incident)
    db.refresh(target_incident)
    db.refresh(main_alert)
    await sio.emit("incident_update", {"type": "undo_drag_link_main_alert", "incident_id": source_incident.id})
    return {
        "message": "Undo drag of main alert completed",
        "source_incident": {"id": source_incident.id, "alert_count": source_incident.alert_count},
        "target_incident": {"id": target_incident.id, "alert_count": target_incident.alert_count}
    }

@app.post("/incidents/{target_incident_id}/bulk_link_main_alerts")
async def bulk_link_main_alerts(target_incident_id: int, payload: BulkLinkMainAlertsPayload, db: SessionLocal = Depends(get_db)):
    target_incident = db.query(Incident).filter(Incident.id == target_incident_id).first()
    if not target_incident:
        raise HTTPException(status_code=404, detail="Target incident not found")
    if target_incident.status == "discarded":
        raise HTTPException(status_code=400, detail="Cannot link main alerts to a discarded incident.")

    now = datetime.utcnow()
    total_added = 0
    moved_alerts = []
    transferred_from_incidents = set()

    for ma_id in payload.main_alert_ids:
        main_alert = db.query(MainAlert).filter(MainAlert.id == ma_id).first()
        if not main_alert:
            continue
        if main_alert.incident_id == target_incident.id:
            continue

        old_incident = None
        if main_alert.incident_id:
            old_incident = db.query(Incident).filter(Incident.id == main_alert.incident_id).first()

        if old_incident and old_incident.definitively_resolved:
            continue

        main_alert.incident_id = target_incident.id
        total_added += main_alert.counter
        target_incident.last_alert_time = now
        moved_alerts.append({
            "id": main_alert.id,
            "message": main_alert.message,
            "counter": main_alert.counter,
            "last_linked_time": main_alert.last_linked_time,
        })
        db.commit()
        db.refresh(main_alert)

        if old_incident and old_incident.id != target_incident.id:
            transferred_from_incidents.add(old_incident.id)

    for old_incident_id in transferred_from_incidents:
        old_incident = db.query(Incident).filter(Incident.id == old_incident_id).first()
        if not old_incident:
            continue
        for comment in old_incident.comments:
            exists = any(c.comment_text == comment.comment_text and c.login_name == comment.login_name for c in target_incident.comments)
            if not exists:
                new_comment = IncidentComment(
                    incident_id=target_incident.id,
                    login_name=comment.login_name,
                    comment_text=comment.comment_text
                )
                db.add(new_comment)
        remaining = db.query(MainAlert).filter(MainAlert.incident_id == old_incident.id).count()
        if remaining == 0 and not old_incident.definitively_resolved:
            old_incident.status = "discarded"
        db.commit()
        db.refresh(old_incident)

    target_incident.alert_count += total_added
    db.commit()
    db.refresh(target_incident)
    await sio.emit("incident_update", {"type": "bulk_link_main_alerts", "incident_id": target_incident.id})
    return {
        "message": "Bulk linking completed",
        "incident": {
            "id": target_incident.id,
            "incident_name": target_incident.incident_name,
            "alert_count": target_incident.alert_count,
            "last_alert_time": target_incident.last_alert_time
        },
        "moved_main_alerts": moved_alerts
    }

@app.post("/incidents/{incident_id}/comments/")
async def add_incident_comment(incident_id: int, comment: IncidentCommentCreate, db: SessionLocal = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    new_comment = IncidentComment(
        incident_id=incident_id,
        login_name=comment.login_name,
        comment_text=comment.comment_text
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    await sio.emit("incident_update", {"type": "add_comment", "incident_id": incident.id})
    return new_comment

@app.patch("/incidents/{incident_id}/comments/{comment_id}")
async def update_incident_comment(incident_id: int, comment_id: int, payload: IncidentCommentUpdate, db: SessionLocal = Depends(get_db)):
    comment = db.query(IncidentComment).filter(
        IncidentComment.id == comment_id,
        IncidentComment.incident_id == incident_id
    ).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    comment.comment_text = payload.comment_text
    db.commit()
    db.refresh(comment)
    await sio.emit("incident_update", {"type": "update_comment", "incident_id": incident_id})
    return comment

@app.delete("/incidents/{incident_id}/comments/{comment_id}")
async def delete_incident_comment(incident_id: int, comment_id: int, db: SessionLocal = Depends(get_db)):
    comment = db.query(IncidentComment).filter(
        IncidentComment.id == comment_id,
        IncidentComment.incident_id == incident_id
    ).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(comment)
    db.commit()
    await sio.emit("incident_update", {"type": "delete_comment", "incident_id": incident_id})
    return {"detail": "Comment deleted"}

@app.post("/incidents/{target_incident_id}/drag_transfer/{source_incident_id}")
async def drag_transfer_incident(target_incident_id: int, source_incident_id: int, db: SessionLocal = Depends(get_db)):
    target_incident = db.query(Incident).filter(Incident.id == target_incident_id).first()
    source_incident = db.query(Incident).filter(Incident.id == source_incident_id).first()
    if not target_incident or not source_incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if target_incident.status == "discarded":
        raise HTTPException(status_code=400, detail="Cannot transfer into a discarded incident")
    now = datetime.utcnow()
    total_added = 0
    moved_alerts = []
    for ma in source_incident.main_alerts:
        ma.incident_id = target_incident.id
        total_added += ma.counter
        target_incident.last_alert_time = now
        moved_alerts.append({
            "id": ma.id,
            "message": ma.message,
            "counter": ma.counter,
            "last_linked_time": ma.last_linked_time
        })
    for comment in source_incident.comments:
        exists = any(c.comment_text == comment.comment_text and c.login_name == comment.login_name for c in target_incident.comments)
        if not exists:
            new_comment = IncidentComment(
                incident_id=target_incident.id,
                login_name=comment.login_name,
                comment_text=comment.comment_text
            )
            db.add(new_comment)
    source_incident.status = "discarded"
    target_incident.alert_count += total_added
    db.commit()
    db.refresh(target_incident)
    await sio.emit("incident_update", {"type": "drag_transfer", "incident_id": target_incident.id})
    return {
        "message": "Incident transferred via drag & drop",
        "incident": {
            "id": target_incident.id,
            "incident_name": target_incident.incident_name,
            "alert_count": target_incident.alert_count,
            "last_alert_time": target_incident.last_alert_time
        },
        "moved_main_alerts": moved_alerts
    }

@app.post("/incidents/{target_incident_id}/undo_drag_transfer/{source_incident_id}")
async def undo_drag_transfer(target_incident_id: int, source_incident_id: int, payload: BulkLinkMainAlertsPayload, db: SessionLocal = Depends(get_db)):
    target_incident = db.query(Incident).filter(Incident.id == target_incident_id).first()
    source_incident = db.query(Incident).filter(Incident.id == source_incident_id).first()
    if not target_incident or not source_incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    total_removed = 0
    moved_alerts = []
    for ma_id in payload.main_alert_ids:
        main_alert = db.query(MainAlert).filter(MainAlert.id == ma_id).first()
        if main_alert and main_alert.incident_id == target_incident.id:
            main_alert.incident_id = source_incident.id
            total_removed += main_alert.counter
            moved_alerts.append({
                "id": main_alert.id,
                "message": main_alert.message,
                "counter": main_alert.counter,
                "last_linked_time": main_alert.last_linked_time,
            })
    target_incident.alert_count -= total_removed
    source_incident.alert_count += total_removed
    for comment in source_incident.comments:
        for t_comment in list(target_incident.comments):
            if t_comment.comment_text == comment.comment_text and t_comment.login_name == comment.login_name:
                db.delete(t_comment)
    if source_incident.status in ("discarded", "resolved"):
        source_incident.status = "open"
    db.commit()
    db.refresh(target_incident)
    db.refresh(source_incident)
    await sio.emit("incident_update", {"type": "undo_drag_transfer", "incident_id": target_incident.id})
    return {
        "message": "Undo drag transfer completed",
        "target_incident": {
            "id": target_incident.id,
            "alert_count": target_incident.alert_count
        },
        "source_incident": {
            "id": source_incident.id,
            "alert_count": source_incident.alert_count
        },
        "moved_alerts": moved_alerts
    }

@app.patch("/incidents/{incident_id}/resolve")
async def resolve_incident(incident_id: int, db: SessionLocal = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.status = "resolved"
    incident.last_resolved_time = datetime.utcnow()
    if not incident.first_resolved_time:
        incident.first_resolved_time = datetime.utcnow()
    db.commit()
    db.refresh(incident)
    await sio.emit("incident_update", {"type": "definitively_resolve", "incident_id": incident.id})
    return incident

@app.patch("/incidents/{incident_id}/definitively_resolve")
async def definitively_resolve_incident(incident_id: int, db: SessionLocal = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.status = "resolved"
    incident.last_resolved_time = datetime.utcnow()
    if not incident.first_resolved_time:
        incident.first_resolved_time = datetime.utcnow()
    incident.definitively_resolved = True
    db.commit()
    db.refresh(incident)
    await sio.emit("incident_update", {"type": "reopen", "incident_id": incident.id})
    return incident

@app.patch("/incidents/{incident_id}/reopen")
async def reopen_incident(incident_id: int, db: SessionLocal = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if incident.definitively_resolved:
        raise HTTPException(status_code=400, detail="Incident is definitively resolved and cannot be reopened.")
    if incident.status == "discarded":
        raise HTTPException(status_code=400, detail="Cannot reopen a discarded incident.")
    incident.status = "open"
    incident.reopened_time = datetime.utcnow()
    incident.reopen_count += 1
    db.commit()
    db.refresh(incident)
    await sio.emit("incident_update", {"type": "reopen", "incident_id": incident.id})
    return incident

@app.patch("/incidents/{incident_id}/rename")
async def rename_incident(incident_id: int, payload: IncidentRename, db: SessionLocal = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.incident_name = payload.new_name
    db.commit()
    db.refresh(incident)
    await sio.emit("incident_update", {"type": "rename", "incident_id": incident.id})
    return incident

@app.patch("/incidents/{incident_id}/update_severity")
async def update_severity(incident_id: int, payload: IncidentUpdateSeverity, db: SessionLocal = Depends(get_db)):
    allowed = {"MAJOR", "HIGH", "MEDIUM", "LOW"}
    if payload.severity not in allowed:
        raise HTTPException(status_code=400, detail="Invalid severity value")
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if incident.status != "open":
        raise HTTPException(status_code=400, detail="Severity can only be updated on open incidents.")
    incident.severity = payload.severity
    db.commit()
    db.refresh(incident)
    await sio.emit("incident_update", {"type": "update_severity", "incident_id": incident.id})
    return incident

@app.patch("/incidents/{incident_id}/update_team")
async def update_team(incident_id: int, payload: IncidentUpdateTeam, db: SessionLocal = Depends(get_db)):
    allowed_teams = {"team1", "team2", "team3"}
    if payload.team not in allowed_teams:
        raise HTTPException(status_code=400, detail="Invalid team value")
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if incident.status != "open":
        raise HTTPException(status_code=400, detail="Team can only be updated on open incidents.")
    incident.team = payload.team
    db.commit()
    db.refresh(incident)
    await sio.emit("incident_update", {"type": "update_team", "incident_id": incident.id})
    return incident

@app.patch("/incidents/{incident_id}/update_assignee")
async def update_assignee(incident_id: int, payload: IncidentUpdateAssignee, db: SessionLocal = Depends(get_db)):
    allowed_assignees = {"person1", "person2", "person3", "person4"}
    if payload.assignee not in allowed_assignees:
        raise HTTPException(status_code=400, detail="Invalid assignee value")
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if incident.status != "open":
        raise HTTPException(status_code=400, detail="Assignee can only be updated on open incidents.")
    incident.assignee = payload.assignee
    db.commit()
    db.refresh(incident)
    await sio.emit("incident_update", {"type": "update_assignee", "incident_id": incident.id})
    return incident

@app.get("/incidents/")
async def read_incidents(
    status: str = Query("open"),
    team: str = Query(None),
    assignee: str = Query(None),
    severity: str = Query(None),
    db: SessionLocal = Depends(get_db)
):
    query = db.query(Incident).options(joinedload(Incident.main_alerts), joinedload(Incident.comments))
    s = status.lower().strip()
    if s == "all":
        query = query.filter(Incident.status.in_(["open", "resolved"]))
    else:
        query = query.filter(Incident.status == s)
    if team:
        query = query.filter(Incident.team == team)
    if assignee:
        query = query.filter(Incident.assignee == assignee)
    if severity:
        query = query.filter(Incident.severity == severity)
    incidents = query.all()

    results = []
    for inc in incidents:
        main_alerts_info = [{
            "id": ma.id,
            "message": ma.message,
            "counter": ma.counter,
            "last_linked_time": ma.last_linked_time
        } for ma in inc.main_alerts]
        comments_info = [{
            "id": comment.id,
            "login_name": comment.login_name,
            "comment_text": comment.comment_text,
            "created_at": comment.created_at,
            "last_modified": comment.last_modified
        } for comment in inc.comments]
        results.append({
            "id": inc.id,
            "incident_name": inc.incident_name,
            "status": inc.status,
            "severity": inc.severity,
            "wikilink": inc.wikilink,
            "definitively_resolved": inc.definitively_resolved,
            "team": inc.team,
            "assignee": inc.assignee,
            "source": inc.source,     # New field added
            "host": inc.host,         # New field added
            "state": inc.state,       # New field added
            "alert_count": inc.alert_count,
            "reopen_count": inc.reopen_count,
            "first_alert_time": inc.first_alert_time,
            "last_alert_time": inc.last_alert_time,
            "first_resolved_time": inc.first_resolved_time,
            "last_resolved_time": inc.last_resolved_time,
            "reopened_time": inc.reopened_time,
            "main_alerts": main_alerts_info,
            "comments": comments_info
        })
    return results

@app.get("/check_permission/")
async def check_permission(role: str):
    if casbin_enforcer.enforce(role, "/incidents", "create"):
        return {"permission": "granted"}
    else:
        raise HTTPException(status_code=403, detail="Permission denied")

# -------------------------
# Run the application via socket_app
# -------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:socket_app", host="0.0.0.0", port=8000, reload=True)
