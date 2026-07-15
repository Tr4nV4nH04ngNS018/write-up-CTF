# 🏆 CTF Writeups Collection

Welcome to my repository of Capture The Flag (CTF) writeups. This repository contains detailed solutions, explanations, and scripts for various security challenges across different categories.

---

## 📊 Statistics

| Category | Solved | Status |
| :--- | :---: | :---: |
| **🌐 Web Exploitation** | 3 | 🟢 Complete |
| **⚙️ Reverse Engineering** | 8 | 🟢 Complete |
| **🔍 Forensics** | 1 | 🟢 Complete |
| **🔐 Cryptography** | 1 | 🟢 Complete |
| **📁 Other Events** | 2 | 🟢 Complete |
| **🔥 Total** | **15** | **Active** |

---

## 📂 Challenges Directory

### 🌐 Web Exploitation

| Challenge | Key Concepts / Techniques | Flag |
| :--- | :--- | :--- |
| [Double SQL Injection to PostgreSQL File Read](writeups/web/Double-SQLi-PostgreSQL-File-Read.md) | Auth Bypass, UNION-based SQLi, PostgreSQL `pg_read_file()` | <details><summary>Reveal Flag</summary><code>VSL{d0ubl3_sqli_t0_p0stgr3s_rc3_8d2f19}</code></details> |
| [B1tsy-Ducky](writeups/web/B1tsy-Ducky.md) | Go WebAssembly, Web + Reverse Engineering | <details><summary>Reveal Flag</summary><code>v1t{b1tsy_t1psy_duck_w4sm}</code></details> |
| [Duck Nettool Revenge](writeups/web/Duck-Nettool-Revenge.md) | Command Injection, Bypass Restriction with Wildcards | <details><summary>Reveal Flag</summary><code>v1t{br0_th15_15_duck}</code></details> |

<br>

### ⚙️ Reverse Engineering

| Challenge | Key Concepts / Techniques | Flag |
| :--- | :--- | :--- |
| [Keyfile Authentication](writeups/reverse/Keyfile-Authentication.md) | Keyfile verification logic, Struct Alignment, Endianness | <details><summary>Reveal Flag</summary><code>FLAG{f1l3_p4rs1ng_m4st3ry}</code></details> |
| [Easy Keygen](<Easy keygen/readme.md>) | Rotating XOR cipher decoding | <details><summary>Reveal Flag</summary><code>K3ygenm3</code></details> |
| [Easy Crack](Easy_Crack/README.md) | String search, local variable tracking, comparison logic | <details><summary>Reveal Flag</summary><code>Ea5yR3versing</code></details> |
| [Classless](writeups/reverse/Classless.md) | Misc + RE, ELF Virtual Machine, Virtual Tables | <details><summary>Reveal Flag</summary><code>v1t{trilingual_vtable_babel_6f01a2c9}</code></details> |
| [Diddy License Checker](writeups/reverse/Diddy-License-Checker.md) | AES Key Scheduling, Fibonacci Sequence, ELF License Checker | <details><summary>Reveal Flag</summary><code>v1t{435_f1b0_w3bs1t3}</code></details> |
| [Ducks Ping-Pong](writeups/reverse/Ducks-Ping-Pong.md) | Windows Kernel Driver, User-mode Client Communication | <details><summary>Reveal Flag</summary><code>v1t{quack_quack_D1ngp0ng_ducks!}</code></details> |
| [TINY](writeups/reverse/TINY.md) | Custom ELF, Self-Decryption, Run-Length Encoding (RLE) | <details><summary>Reveal Flag</summary><code>v1t{^}</code></details> |
| [TRY](writeups/reverse/TRY.md) | Tiny C Compiler Obfuscation, VM Interpreter | <details><summary>Reveal Flag</summary><code>v1t{n0_dump_just_pain}</code></details> |

<br>

### 🔍 Forensics

| Challenge | Key Concepts / Techniques | Flag |
| :--- | :--- | :--- |
| [Basic QnA](writeups/forensics/Basic-QnA.md) | Packet Analysis, Network forensics | <details><summary>Reveal Flag</summary><code>v1t{llm_c0uld_s0lv3_th1s_ez_chall3ng3!!!}</code></details> |

<br>

### 🔐 Cryptography

| Challenge | Key Concepts / Techniques | Flag |
| :--- | :--- | :--- |
| [Hextrap](writeups/crypto/Hextrap.md) | Math, Hexagonal transformations, smooth orders | <details><summary>Reveal Flag</summary><code>v1t{six_twists_one_smooth_order}</code></details> |

<br>

### 📂 CTF HACKTHEON SEJONG 2026

| Challenge / Writeup | Document Link |
| :--- | :--- |
| **Recover It!** | [Recover It!.docx](<CTF HACKTHEON SEJONG 2026/Recover It!.docx>) |
| **immutable** | [immutable.docx](<CTF HACKTHEON SEJONG 2026/immutable.docx>) |

---

## 🛠️ Usage & Setup

This repository is organized logically into folders. To inspect a writeup:
1. Navigate to `writeups/` and select a category folder.
2. Open the corresponding `.md` file to view the full walkthrough, commands, and code.
3. Python solvers and other artifacts are available under their respective directories where applicable.
