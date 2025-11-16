# KOYUN - Cloudflare Tunnel Relay Panel (v0.2.0)

基于 FastAPI + MySQL + Docker 的 Cloudflare Tunnel 中转面板。  
支持管理节点、配置 TCP/UDP 规则，并自动生成 cloudflared 的 `config.yml` 片段。

## 部署步骤

```bash
git clone https://github.com/xiaofujie369/koyun
cd koyun
cp .env.example .env
docker compose up -d
