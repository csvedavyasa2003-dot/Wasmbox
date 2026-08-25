\# WasmBox Setup Guide



\## 1. Project Overview



WasmBox is a secure multi-tenant WebAssembly plugin sandbox designed to execute untrusted customer plugins in an isolated environment.



The project is organized into separate components for backend integration, compilation, runtime execution, security, frontend development, testing, and documentation.



\## 2. Project Structure



```text

WasmBox/

├── backend/

│   └── app/

│       ├── api/

│       │   └── routes/

│       │       ├── compile.py

│       │       ├── execute.py

│       │       └── plugins.py

│       ├── services/

│       │   ├── compiler\_service.py

│       │   └── runtime\_service.py

│       ├── main.py

│       └── requirements.txt

│

├── compiler/

├── runtime/

├── security/

├── frontend/

├── tests/

├── docs/

├── docker-compose.yml

├── .gitignore

└── README.md

