from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
import enum


class NodeType(str, enum.Enum):
  relay = "relay"   # 中转节点
  exit = "exit"     # 落地节点


class Node(Base):
  __tablename__ = "nodes"

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String(64), unique=True, index=True)  # 节点名，如 HK-Relay-1
  host = Column(String(128))                          # IP 或域名，仅备注用
  description = Column(String(255), default="")
  node_type = Column(Enum(NodeType), default=NodeType.relay)
  bandwidth_mbps = Column(Integer, default=100)

  tunnels = relationship("TunnelRule", back_populates="node")


class TunnelRule(Base):
  __tablename__ = "tunnel_rules"

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String(64), index=True)          # 规则名
  hostname = Column(String(128))                 # cloudflared ingress 用的 hostname
  protocol = Column(String(8), default="tcp")    # tcp / udp
  upstream_host = Column(String(128))            # 本地目标 host
  upstream_port = Column(Integer)                # 本地目标端口
  enabled = Column(Boolean, default=True)

  node_id = Column(Integer, ForeignKey("nodes.id"))
  node = relationship("Node", back_populates="tunnels")
