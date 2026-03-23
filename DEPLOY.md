# PMS Generator - Deployment Guide

## Local Development

### Quick Start
```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the FastAPI server
python3 main_api.py
```
Open http://localhost:8080 in your browser.

### CLI Mode (standalone)
```bash
python3 main.py --demo
```

---

## Docker Deployment

### Build and Run
```bash
cd deploy
docker-compose up --build -d
```
Access at http://localhost:8080

### Stop
```bash
docker-compose down
```

---

## Render Deployment

1. Push your code to a GitHub repository
2. Go to https://render.com and create a new Web Service
3. Connect your GitHub repo
4. Render will auto-detect the `deploy/render.yaml` config
5. Alternatively, configure manually:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn api.app:app --host 0.0.0.0 --port $PORT`
   - **Python Version:** 3.11

---

## AWS Deployment (EC2)

### Setup
```bash
# SSH into your EC2 instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Install Python 3.11
sudo yum install python3.11 python3.11-pip -y

# Clone repository
git clone https://github.com/your-repo/pms-generator.git
cd pms-generator

# Install dependencies
pip3.11 install -r requirements.txt

# Run with nohup (background)
nohup python3.11 -m uvicorn api.app:app --host 0.0.0.0 --port 8080 &
```

### With systemd (production)
Create `/etc/systemd/system/pms-generator.service`:
```ini
[Unit]
Description=PMS Generator FastAPI
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/pms-generator
ExecStart=/usr/bin/python3.11 -m uvicorn api.app:app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable pms-generator
sudo systemctl start pms-generator
```

---

## Environment Notes

- **Database:** SQLite (auto-created as `pms_generator.db` in project root)
- **Output files:** Generated Excel files are saved to `output/` directory
- **No external database required** - everything runs self-contained
- **Port:** Default 8080 (configurable via `main_api.py` or `$PORT` env var)

## API Documentation

Once running, visit:
- **Swagger UI:** http://localhost:8080/docs
- **ReDoc:** http://localhost:8080/redoc
