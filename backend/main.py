from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .database import SessionLocal, engine, Base
from . import models, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="KOYUN API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/nodes", response_model=List[schemas.NodeOut])
def list_nodes(db: Session = Depends(get_db)):
    return db.query(models.Node).all()


@app.post("/nodes", response_model=schemas.NodeOut)
def create_node(node: schemas.NodeCreate, db: Session = Depends(get_db)):
    db_node = models.Node(**node.dict())
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node


@app.get("/tunnels", response_model=List[schemas.TunnelOut])
def list_tunnels(db: Session = Depends(get_db)):
    return db.query(models.TunnelRule).all()


@app.post("/tunnels", response_model=schemas.TunnelOut)
def create_tunnel(tunnel: schemas.TunnelCreate, db: Session = Depends(get_db)):
    node = db.query(models.Node).get(tunnel.node_id)
    if not node:
        raise HTTPException(400, "Node not found")
    db_tunnel = models.TunnelRule(**tunnel.dict())
    db.add(db_tunnel)
    db.commit()
    db.refresh(db_tunnel)
    return db_tunnel


@app.get("/nodes/{node_id}/cloudflared-config")
def cloudflared_config(node_id: int, db: Session = Depends(get_db)):
    node = db.query(models.Node).get(node_id)
    if not node:
        raise HTTPException(404, "Node not found")

    tunnels = db.query(models.TunnelRule).filter(
        models.TunnelRule.node_id == node_id,
        models.TunnelRule.enabled == True
    ).all()

    ingress = "\n".join(
        f"  - hostname: {t.hostname}\n    service: {t.protocol}://{t.upstream_host}:{t.upstream_port}"
        for t in tunnels
    )

    config = (
        "tunnel: YOUR_TUNNEL_NAME\n"
        "ingress:\n"
        f"{ingress}\n"
        "  - service: http_status:404\n"
    )

    return {"node": node.name, "config": config}
