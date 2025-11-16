from pydantic import BaseModel
from typing import Optional
from enum import Enum


class NodeType(str, Enum):
    relay = "relay"
    exit = "exit"


class NodeBase(BaseModel):
    name: str
    host: str
    description: Optional[str] = ""
    node_type: NodeType = NodeType.relay
    bandwidth_mbps: int = 100


class NodeCreate(NodeBase):
    pass


class NodeUpdate(BaseModel):
    name: Optional[str] = None
    host: Optional[str] = None
    description: Optional[str] = None
    node_type: Optional[NodeType] = None
    bandwidth_mbps: Optional[int] = None


class NodeOut(NodeBase):
    id: int

    class Config:
        orm_mode = True


class TunnelBase(BaseModel):
    name: str
    hostname: str
    protocol: str = "tcp"
    upstream_host: str
    upstream_port: int
    node_id: int
    enabled: bool = True


class TunnelCreate(TunnelBase):
    pass


class TunnelUpdate(BaseModel):
    name: Optional[str] = None
    hostname: Optional[str] = None
    protocol: Optional[str] = None
    upstream_host: Optional[str] = None
    upstream_port: Optional[int] = None
    node_id: Optional[int] = None
    enabled: Optional[bool] = None


class TunnelOut(TunnelBase):
    id: int

    class Config:
        orm_mode = True
