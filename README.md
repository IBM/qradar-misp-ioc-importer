# MISP IOC Importer for QRadar

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![QRadar](https://img.shields.io/badge/QRadar-7.3+-red.svg)](https://www.ibm.com/products/qradar-siem)
[![MISP](https://img.shields.io/badge/MISP-2.4+-green.svg)](https://www.misp-project.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

> Automate threat intelligence import from MISP into IBM QRadar SIEM reference sets

---

## Overview

This QRadar application enables seamless integration between MISP (Malware Information Sharing Platform) and IBM QRadar SIEM, automatically importing Indicators of Compromise (IOCs) into QRadar reference sets for enhanced threat detection.

**Key Features:**
- ✅ Automated IOC synchronization from MISP to QRadar
- ✅ Configurable polling intervals
- ✅ Real-time monitoring dashboard
- ✅ Operational logging system
- ✅ Flexible deployment (QRadar App or Docker)

---

## Quick Start

### Prerequisites
- IBM QRadar SIEM 7.3+
- QRadar App Framework SDK v2.0+
- MISP instance with API access
- Python 3.7+

### Installation

**Deploy to QRadar:**
```bash
# Package application
qapp package -p mispimporter.zip

# Deploy to QRadar
qapp deploy -q <QRadar_server> -u <QRadar_user> -p mispimporter.zip
```

**Run with Docker:**
```bash
docker build -t misp-qradar-importer .
docker run -p 5000:5000 misp-qradar-importer
```

---

## Configuration

| Parameter | Description | Example |
|-----------|-------------|---------|
| **MISP Server** | MISP instance URL | `https://misp.example.com` |
| **MISP API Key** | Authentication token | `your-api-key` |
| **QRadar Server** | QRadar console URL | `https://qradar.example.com` |
| **QRadar API Key** | SEC token | `your-token` |
| **Reference Set** | Target reference set | `MISP_IOCs` |
| **Polling Interval** | Sync frequency (seconds) | `300` |
| **Event ID** | MISP event to import | `123` |
| **IOC Type** | Indicator types | `ip-src`, `domain`, `url` |

---

## Usage

1. Navigate to **QRadar → Admin → Extension Management**
2. Open **MISP IOC Importer** application
3. Configure connection parameters
4. Click **"Import IOCs"** to start synchronization
5. Monitor import status in dashboard

---

## Documentation

- [QRadar App Framework SDK](https://www.ibm.com/support/pages/qradar-whats-new-app-framework-sdk-v200)
- [MISP API Documentation](https://www.misp-project.org/openapi/)
- [Application Manual](app-documentation.pdf)

---

## Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## License

GPL-3.0 License - See [LICENSE](LICENSE) file

---

## Support

- [Report Issues](https://github.com/IBM/qradar-misp-ioc-importer/issues)
- [IBM Security](https://www.ibm.com/security)

---

**Developed and maintained by IBM Security**
