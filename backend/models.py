from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
import enum


class NodeType(str, enum.Enum):
    relay = "relay"
    exit = "exit"


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, index=True)
    host = Column(String(128))
    description = Column(String(255), default="")
    node_type = Column(Enum(NodeType), default=NodeType.relay)
    bandwidth_mbps = Column(Integer, default=100)

    tunnels = relationship("TunnelRule", back_populates="node")


class TunnelRule(Base):
    __tablename__ = "tunnel_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), index=True)
    hostname = Column(String(128))
    protocol = Column(String(8), default="tcp")
    upstream_host = Column(String(128))
    upstream_port = Column(Integer)
    enabled = Column(Boolean, default=True)

    node_id = Column(Integer, ForeignKey("nodes.id"))
    node = relationship("Node", back_populates="tunnels")
