from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from .database import SessionLocal, engine, Base
from . import models, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="KOYUN API",
    version="0.2.0",
    description="KOYUN - Cloudflare Tunnel Relay Panel backend",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CORS（开发阶段先全放开，生产可改）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.2.0"}


# --- Node APIs ---

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


@app.put("/nodes/{node_id}", response_model=schemas.NodeOut)
def update_node(node_id: int, node: schemas.NodeUpdate, db: Session = Depends(get_db)):
    db_node = db.query(models.Node).get(node_id)
    if not db_node:
        raise HTTPException(status_code=404, detail="Node not found")
    for k, v in node.dict(exclude_unset=True).items():
        setattr(db_node, k, v)
    db.commit()
    db.refresh(db_node)
    return db_node


@app.delete("/nodes/{node_id}")
def delete_node(node_id: int, db: Session = Depends(get_db)):
    db_node = db.query(models.Node).get(node_id)
    if not db_node:
        raise HTTPException(status_code=404, detail="Node not found")
    db.delete(db_node)
    db.commit()
    return {"ok": True}


# --- Tunnel APIs ---

@app.get("/tunnels", response_model=List[schemas.TunnelOut])
def list_tunnels(db: Session = Depends(get_db)):
    return db.query(models.TunnelRule).all()


@app.post("/tunnels", response_model=schemas.TunnelOut)
def create_tunnel(tunnel: schemas.TunnelCreate, db: Session = Depends(get_db)):
    node = db.query(models.Node).get(tunnel.node_id)
    if not node:
        raise HTTPException(status_code=400, detail="Node not found")
    db_tunnel = models.TunnelRule(**tunnel.dict())
    db.add(db_tunnel)
    db.commit()
    db.refresh(db_tunnel)
    return db_tunnel


@app.put("/tunnels/{tunnel_id}", response_model=schemas.TunnelOut)
def update_tunnel(tunnel_id: int, tunnel: schemas.TunnelUpdate, db: Session = Depends(get_db)):
    db_tunnel = db.query(models.TunnelRule).get(tunnel_id)
    if not db_tunnel:
        raise HTTPException(status_code=404, detail="Tunnel not found")
    for k, v in tunnel.dict(exclude_unset=True).items():
        setattr(db_tunnel, k, v)
    db.commit()
    db.refresh(db_tunnel)
    return db_tunnel


@app.delete("/tunnels/{tunnel_id}")
def delete_tunnel(tunnel_id: int, db: Session = Depends(get_db)):
    db_tunnel = db.query(models.TunnelRule).get(tunnel_id)
    if not db_tunnel:
        raise HTTPException(status_code=404, detail="Tunnel not found")
    db.delete(db_tunnel)
    db.commit()
    return {"ok": True}


# --- cloudflared config generator ---

@app.get("/nodes/{node_id}/cloudflared-config")
def cloudflared_config(node_id: int, db: Session = Depends(get_db)):
    node = db.query(models.Node).get(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    tunnels = db.query(models.TunnelRule).filter(
        models.TunnelRule.node_id == node_id,
        models.TunnelRule.enabled == True
    ).all()

    ingress_lines = []
    for t in tunnels:
        # 支持 tcp/udp
        proto = t.protocol.lower()
        if proto not in ("tcp", "udp"):
            proto = "tcp"
        service = f"{proto}://{t.upstream_host}:{t.upstream_port}"
        ingress_lines.append(f"  - hostname: {t.hostname}\n    service: {service}")

    config = "tunnel: YOUR_TUNNEL_NAME\n\ningress:\n"
    if ingress_lines:
        config += "\n".join(ingress_lines) + "\n"
    config += "  - service: http_status:404\n"

    return {
        "node": node.name,
        "config": config,
    }
