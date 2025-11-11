# Installation Guide for OpenLCA MCP Server

Quick installation guide for the OpenLCA MCP Server.

## Prerequisites

### Required Software

1. **Python 3.10 or higher**
   ```bash
   python --version  # Should show 3.10 or higher
   ```

2. **openLCA Desktop Application (v2.x)**
   - Download from [openlca.org](https://www.openlca.org/download/)
   - Install for your platform
   - Open and verify it works

3. **pip (Python package manager)**
   ```bash
   pip --version  # Usually comes with Python
   ```

### Optional (for n8n integration)

4. **n8n workflow automation**
   - Self-hosted or cloud instance
   - Version with MCP support

## Installation Steps

### 1. Navigate to MCP Server Directory

```bash
cd mcp-server
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `mcp` - Model Context Protocol SDK
- `pydantic` - Data validation
- `python-dotenv` - Environment configuration
- `openlca-ipc` - Parent library (from `../`)

**Expected output:**
```
Successfully installed mcp-0.9.0 pydantic-2.5.0 python-dotenv-1.0.0 ...
```

### 3. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit configuration (optional)
nano .env
```

**Default `.env` settings:**
```bash
OPENLCA_PORT=8080          # Match your IPC server port
OPENLCA_HOST=localhost     # Usually localhost
LOG_LEVEL=INFO             # DEBUG, INFO, WARNING, ERROR
```

### 4. Verify Installation

```bash
python -m src.server
```

**Expected output:**
```
Starting OpenLCA MCP Server...
OpenLCA port: 8080
✓ Successfully connected to openLCA
MCP Server running...
```

Press `Ctrl+C` to stop.

## Verification Checklist

After installation, verify:

- [ ] Python 3.10+ installed
- [ ] Dependencies installed without errors
- [ ] `.env` file created and configured
- [ ] Server starts without errors
- [ ] openLCA connection successful

## Platform-Specific Notes

### Windows

```bash
# Use Python launcher if needed
py -m pip install -r requirements.txt
py -m src.server
```

**Path in .env (Windows):**
```bash
# Use forward slashes or escaped backslashes
MCP_SERVER_PATH=D:/path/to/mcp-server
# or
MCP_SERVER_PATH=D:\\path\\to\\mcp-server
```

### macOS

```bash
# May need python3 explicitly
python3 -m pip install -r requirements.txt
python3 -m src.server
```

**Path in .env (macOS):**
```bash
MCP_SERVER_PATH=/Users/username/path/to/mcp-server
```

### Linux

```bash
# Install Python dev headers if needed
sudo apt install python3-dev python3-pip  # Ubuntu/Debian
sudo yum install python3-devel python3-pip  # CentOS/RHEL

# Then install dependencies
pip3 install -r requirements.txt
python3 -m src.server
```

**Path in .env (Linux):**
```bash
MCP_SERVER_PATH=/home/username/path/to/mcp-server
```

## Troubleshooting Installation

### Issue: pip install fails

**Error:**
```
ERROR: Could not find a version that satisfies the requirement mcp>=0.9.0
```

**Solutions:**
1. Update pip:
   ```bash
   pip install --upgrade pip
   ```

2. Use specific Python version:
   ```bash
   python3.11 -m pip install -r requirements.txt
   ```

3. Install in virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Issue: Cannot import openlca_ipc

**Error:**
```
ModuleNotFoundError: No module named 'openlca_ipc'
```

**Solution:**

The parent library needs to be installed:

```bash
# Go to parent directory
cd ..

# Install openlca-ipc library
pip install -e .

# Return to mcp-server
cd mcp-server

# Try again
python -m src.server
```

### Issue: Server starts but can't connect to openLCA

**Error:**
```
✗ Failed to connect to openLCA: Connection refused
```

**Solutions:**

1. **Start openLCA Desktop:**
   - Launch the application
   - Open a database

2. **Start IPC Server:**
   - In openLCA: Tools → Developer Tools → IPC Server
   - Click "Start"

3. **Check port number:**
   - Look at IPC server window for port
   - Update `.env` to match:
     ```bash
     OPENLCA_PORT=8080  # or whatever port is shown
     ```

4. **Restart MCP server:**
   ```bash
   python -m src.server
   ```

## Using Virtual Environments (Recommended)

### Create Virtual Environment

```bash
# In mcp-server directory
python -m venv venv
```

### Activate

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Deactivate When Done

```bash
deactivate
```

## Development Installation

For development and testing:

```bash
# Install with development dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio black ruff

# Install parent library in editable mode
cd ..
pip install -e .
cd mcp-server
```

## Docker Installation (Advanced)

Create `Dockerfile` in `mcp-server/`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy parent library
COPY ../ /parent

# Install parent library
RUN pip install -e /parent

# Copy MCP server
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Set environment
ENV OPENLCA_PORT=8080
ENV LOG_LEVEL=INFO

# Run server
CMD ["python", "-m", "src.server"]
```

Build and run:

```bash
docker build -t openlca-mcp-server .
docker run -p 8080:8080 openlca-mcp-server
```

**Note:** openLCA must be accessible from container.

## Verifying Tools Available

After installation, verify tools are available:

```bash
# Install MCP inspector (optional)
npm install -g @modelcontextprotocol/inspector

# Inspect server
mcp-inspector python -m src.server
```

This opens a web interface showing all 15+ available tools.

## Next Steps

After successful installation:

1. **Quick Start:** See [docs/quickstart.md](docs/quickstart.md)
2. **n8n Integration:** See [docs/n8n-integration.md](docs/n8n-integration.md)
3. **Examples:** See [examples/](examples/)

## Uninstallation

To remove:

```bash
# Remove Python packages
pip uninstall mcp pydantic python-dotenv openlca-ipc

# Remove directory
cd ..
rm -rf mcp-server
```

## Getting Help

If installation fails:

1. Check Python version: `python --version`
2. Check pip version: `pip --version`
3. Review error messages carefully
4. Check [Troubleshooting](#troubleshooting-installation) section above
5. Create issue: [GitHub Issues](https://github.com/dernestbank/openlca-ipc/issues)
6. Email: dernestbanksch@gmail.com

## System Requirements

**Minimum:**
- Python 3.10+
- 100 MB disk space
- 256 MB RAM
- openLCA 2.x

**Recommended:**
- Python 3.11+
- 500 MB disk space
- 1 GB RAM
- openLCA 2.x with complete database
- n8n for workflow automation

## License

MIT License - See [LICENSE](../LICENSE)
