# WasmBox Security Model

## 1. Security Objective

WasmBox allows users to upload and execute Python plugins. These plugins are treated as **untrusted code** because they are provided by external users.

The main security objective is to execute these plugins inside a restricted WebAssembly sandbox so that a plugin cannot directly access protected server resources.

The sandbox must restrict:

* Server filesystem access
* Network access
* Excessive memory usage
* Excessive execution time
* Resource abuse

The goal is to allow the plugin to execute normally while preventing unauthorized access to the host system and preventing excessive resource consumption.

## 2. Threat Model

WasmBox assumes that a plugin may be malicious or may contain unsafe code. The sandbox must therefore protect the host system from unauthorized plugin behavior.

### 2.1 Filesystem Access

A plugin may attempt to read or modify files on the server.

Example:

```python
open("/etc/passwd")
```

**Required protection:** The plugin must not have direct access to the host filesystem.

### 2.2 Network Access

A plugin may attempt to connect to an external server or service.

**Required protection:** The plugin must not have unrestricted network access.

### 2.3 Infinite Loops

A plugin may contain an infinite loop that never finishes.

Example:

```python
while True:
    pass
```

**Required protection:** Plugin execution must have a maximum execution time. If the timeout is exceeded, execution must be terminated.

### 2.4 Excessive Resource Usage

A plugin may consume excessive memory or other system resources.

**Required protection:** The sandbox must enforce resource limits so that one plugin cannot consume an unreasonable amount of system resources.

### 2.5 Multi-Tenant Isolation

Plugins are provided by different users in a multi-tenant environment.

**Required protection:** A plugin must not be able to use its execution environment to access protected host resources or interfere with other plugins.

## 3. Security Policy

The WasmBox sandbox follows a deny-by-default security policy. Plugins should only receive the capabilities required for their execution.

| Resource         | Policy | Purpose                                    |
| ---------------- | ------ | ------------------------------------------ |
| Host filesystem  | DENY   | Prevent unauthorized file access           |
| Network          | DENY   | Prevent unauthorized external connections  |
| Memory           | LIMIT  | Prevent excessive memory consumption       |
| Execution time   | LIMIT  | Prevent infinite or long-running execution |
| System resources | LIMIT  | Prevent resource abuse                     |

### 3.1 Filesystem Policy

Plugins must not have direct access to the host filesystem.

Host files such as `/etc/passwd`, application files, configuration files, and other server resources must remain inaccessible to the plugin.

### 3.2 Network Policy

Plugins must not have unrestricted network access.

External network connections must be blocked unless an explicitly controlled capability is provided by the system.

### 3.3 Memory Policy

Plugin memory usage must be limited.

The project specification gives an example maximum memory limit of approximately 10 MB. The final limit will be configured and enforced by the sandbox implementation.

### 3.4 Execution Time Policy

Plugin execution must have a timeout.

If a plugin exceeds the allowed execution time, the execution must be terminated.

### 3.5 Resource Abuse Policy

The sandbox must prevent a plugin from consuming excessive system resources and affecting the stability of the WasmBox service.

## 4. Sandbox Architecture

The WasmBox sandbox uses the WebAssembly runtime to isolate untrusted plugin code from the host system.

The basic execution flow is:

```text
User Plugin
    ↓
Python → WASM Compilation
    ↓
WASM Module
    ↓
Wasmtime Sandbox
    ↓
Security & Resource Restrictions
    ↓
Plugin Execution
    ↓
Execution Result
```

### 4.1 WASM Runtime

Wasmtime is responsible for loading and executing the compiled WASM module.

The plugin runs inside the WASM execution environment instead of running directly as native code on the backend server.

### 4.2 Host Isolation

The WASM module must not receive unrestricted access to host resources.

The sandbox controls which host capabilities are available to the plugin.

By default:

* Host filesystem access is denied.
* Network access is denied.
* Memory usage is limited.
* Execution time is limited.
* Resource usage is restricted.

### 4.3 Security Boundary

The WASM sandbox acts as the security boundary between the untrusted plugin and the WasmBox backend.

```text
+-------------------------+
|    Untrusted Plugin     |
+------------+------------+
             |
             v
+-------------------------+
|      WASM Module        |
+------------+------------+
             |
             v
+-------------------------+
|    Wasmtime Sandbox     |
|                         |
| Filesystem     DENY     |
| Network        DENY     |
| Memory         LIMIT    |
| Execution      LIMIT    |
| Resources      LIMIT    |
+------------+------------+
             |
             v
+-------------------------+
|      Host Backend       |
+-------------------------+
```

The plugin must remain inside this security boundary during execution.
