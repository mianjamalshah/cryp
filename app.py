import os
import subprocess
import hashlib
import base64
from pathlib import Path
from datetime import datetime

import streamlit as st

APP_DIR = Path("e2ee_lab_workspace")
APP_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="E2EE Lab for Food Delivery Security", layout="wide")


def run_command(command: list[str], cwd: Path | None = None, input_text: str | None = None):
    try:
        result = subprocess.run(
            command,
            input=input_text,
            text=True,
            capture_output=True,
            cwd=str(cwd) if cwd else None,
            check=False,
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return 127, "", "Command not found. Make sure OpenSSL is installed and available in PATH."
    except Exception as e:
        return 1, "", str(e)


def write_text_file(path: Path, content: str):
    path.write_text(content, encoding="utf-8")


def read_text_file(path: Path):
    if path.exists():
        return path.read_text(encoding="utf-8", errors="replace")
    return ""


def read_binary_preview(path: Path, size: int = 128):
    if not path.exists():
        return ""
    data = path.read_bytes()[:size]
    return data.hex(" ")


def section_header(title: str, description: str):
    st.subheader(title)
    st.write(description)


st.title("End-to-End Encryption Lab App")
st.write(
    "This app helps you run the five cryptography experiments for your Internet Security assignment. "
    "It generates files, runs OpenSSL commands, shows output, and gives you evidence you can use in your report."
)

with st.sidebar:
    st.header("Lab Controls")
    st.write(f"Workspace: `{APP_DIR.resolve()}`")
    if st.button("Check OpenSSL"):
        code, out, err = run_command(["openssl", "version"], cwd=APP_DIR)
        if code == 0:
            st.success(out.strip())
        else:
            st.error(err or "OpenSSL not available")
    st.info("Install Streamlit with: pip install streamlit")
    st.info("Run the app with: streamlit run app.py")


# -----------------------------
# Experiment 1: RSA
# -----------------------------
with st.expander("Experiment 1: RSA-2048 Key Generation and Encryption", expanded=True):
    section_header(
        "RSA-2048 for secure token protection",
        "This experiment shows how asymmetric encryption can protect a sensitive value such as an API token or payment token."
    )

    rsa_plaintext = st.text_input(
        "Plaintext message",
        value="API_TOKEN=QB-ORDER-SECURE-1234",
        key="rsa_plaintext"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("1. Generate RSA keys"):
            priv_path = APP_DIR / "server_private.pem"
            pub_path = APP_DIR / "server_public.pem"
            code, out, err = run_command(
                ["openssl", "genpkey", "-algorithm", "RSA", "-out", str(priv_path), "-pkeyopt", "rsa_keygen_bits:2048"],
                cwd=APP_DIR,
            )
            if code == 0:
                code2, out2, err2 = run_command(
                    ["openssl", "rsa", "-pubout", "-in", str(priv_path), "-out", str(pub_path)],
                    cwd=APP_DIR,
                )
                if code2 == 0:
                    st.success("RSA private and public keys generated.")
                else:
                    st.error(err2)
            else:
                st.error(err)

    with col2:
        if st.button("2. Save plaintext and encrypt"):
            plain_path = APP_DIR / "token.txt"
            enc_path = APP_DIR / "token_encrypted.bin"
            pub_path = APP_DIR / "server_public.pem"
            write_text_file(plain_path, rsa_plaintext)
            if not pub_path.exists():
                st.error("Public key not found. Generate keys first.")
            else:
                code, out, err = run_command(
                    ["openssl", "pkeyutl", "-encrypt", "-pubin", "-inkey", str(pub_path), "-in", str(plain_path), "-out", str(enc_path)],
                    cwd=APP_DIR,
                )
                if code == 0:
                    st.success("Plaintext saved and encrypted.")
                else:
                    st.error(err)

    if st.button("3. Decrypt ciphertext"):
        enc_path = APP_DIR / "token_encrypted.bin"
        dec_path = APP_DIR / "token_decrypted.txt"
        priv_path = APP_DIR / "server_private.pem"
        if not priv_path.exists() or not enc_path.exists():
            st.error("Missing private key or encrypted file.")
        else:
            code, out, err = run_command(
                ["openssl", "pkeyutl", "-decrypt", "-inkey", str(priv_path), "-in", str(enc_path), "-out", str(dec_path)],
                cwd=APP_DIR,
            )
            if code == 0:
                st.success("Ciphertext decrypted successfully.")
            else:
                st.error(err)

    st.code(read_text_file(APP_DIR / "token.txt") or "No plaintext file yet.")
    st.text_area("Encrypted binary preview", value=read_binary_preview(APP_DIR / "token_encrypted.bin"), height=120)
    st.code(read_text_file(APP_DIR / "token_decrypted.txt") or "No decrypted file yet.")

    st.markdown(
        "**What the code does:** `genpkey` creates the RSA private key, `rsa -pubout` extracts the public key, "
        "`pkeyutl -encrypt` encrypts the file with the public key, and `pkeyutl -decrypt` recovers it with the private key."
    )


# -----------------------------
# Experiment 2: AES-256-CBC
# -----------------------------
with st.expander("Experiment 2: AES-256-CBC File Encryption"):
    section_header(
        "AES-256-CBC for data at rest",
        "This experiment shows how symmetric encryption can protect stored customer data and order backups."
    )

    aes_plaintext = st.text_area(
        "Plaintext customer data",
        value="Name: John Doe | Address: 12 London Road | Card: 4111111111111111 | Order: Pizza",
        key="aes_plaintext"
    )
    aes_password = st.text_input("Encryption password", value="test123", type="password")

    if st.button("1. Save plaintext file"):
        write_text_file(APP_DIR / "orders.txt", aes_plaintext)
        st.success("Plaintext file saved.")

    if st.button("2. Encrypt file with AES-256-CBC"):
        plain_path = APP_DIR / "orders.txt"
        enc_path = APP_DIR / "orders.enc"
        if not plain_path.exists():
            st.error("Create the plaintext file first.")
        else:
            code, out, err = run_command(
                ["openssl", "enc", "-aes-256-cbc", "-salt", "-pbkdf2", "-in", str(plain_path), "-out", str(enc_path), "-pass", f"pass:{aes_password}"],
                cwd=APP_DIR,
            )
            if code == 0:
                st.success("File encrypted successfully.")
            else:
                st.error(err)

    if st.button("3. Decrypt AES file"):
        enc_path = APP_DIR / "orders.enc"
        dec_path = APP_DIR / "orders_decrypted.txt"
        if not enc_path.exists():
            st.error("Encrypted file not found.")
        else:
            code, out, err = run_command(
                ["openssl", "enc", "-aes-256-cbc", "-d", "-pbkdf2", "-in", str(enc_path), "-out", str(dec_path), "-pass", f"pass:{aes_password}"],
                cwd=APP_DIR,
            )
            if code == 0:
                st.success("File decrypted successfully.")
            else:
                st.error(err)

    st.code(read_text_file(APP_DIR / "orders.txt") or "No plaintext file yet.")
    st.text_area("Encrypted file hex preview", value=read_binary_preview(APP_DIR / "orders.enc"), height=120)
    st.code(read_text_file(APP_DIR / "orders_decrypted.txt") or "No decrypted file yet.")

    st.markdown(
        "**What the code does:** `enc -aes-256-cbc` applies AES in CBC mode. `-salt` adds randomness. `-pbkdf2` derives the key more securely from the passphrase. "
        "The same password is needed to decrypt the file."
    )


# -----------------------------
# Experiment 3: Hashing and Salting
# -----------------------------
with st.expander("Experiment 3: Password Hashing and Avalanche Effect"):
    section_header(
        "SHA-256, SHA-512, salting, and avalanche effect",
        "This experiment shows that passwords should be stored as hashes, not plaintext. It also shows how one small change creates a very different hash."
    )

    password_1 = st.text_input("Password 1", value="SecurePass123")
    password_2 = st.text_input("Password 2", value="SecurePass124")

    if st.button("Run hashing experiment"):
        salt = os.urandom(16)
        sha256_1 = hashlib.sha256(password_1.encode()).hexdigest()
        sha512_1 = hashlib.sha512(password_1.encode()).hexdigest()
        sha256_2 = hashlib.sha256(password_2.encode()).hexdigest()
        salted = hashlib.sha256(salt + password_1.encode()).hexdigest()

        st.write("Original password:", password_1)
        st.code(sha256_1, language="text")
        st.write("SHA-512 of original password:")
        st.code(sha512_1, language="text")
        st.write("Second password with one small change:", password_2)
        st.code(sha256_2, language="text")
        st.write("Salt in hex:")
        st.code(salt.hex(), language="text")
        st.write("Salted SHA-256:")
        st.code(salted, language="text")

        st.markdown(
            "**What the code does:** `hashlib.sha256()` and `hashlib.sha512()` create one-way hashes. `os.urandom(16)` generates a random 16-byte salt. "
            "Adding the salt before hashing makes matching attacks harder."
        )


# -----------------------------
# Experiment 4: Certificate and PKI
# -----------------------------
with st.expander("Experiment 4: SSL/TLS Certificate and Mini PKI"):
    section_header(
        "Generate a private key, CSR, and self-signed certificate",
        "This experiment shows how a food delivery server can create identity material for HTTPS."
    )

    cn = st.text_input("Common Name (CN)", value="www.quickbite.co.uk")
    org = st.text_input("Organization (O)", value="QuickBite Food Delivery Ltd")
    country = st.text_input("Country (C)", value="GB")

    if st.button("1. Generate server key"):
        code, out, err = run_command(
            ["openssl", "genpkey", "-algorithm", "RSA", "-out", str(APP_DIR / "server.key"), "-pkeyopt", "rsa_keygen_bits:2048"],
            cwd=APP_DIR,
        )
        if code == 0:
            st.success("Server private key generated.")
        else:
            st.error(err)

    if st.button("2. Create CSR"):
        subject = f"/CN={cn}/O={org}/C={country}"
        if not (APP_DIR / "server.key").exists():
            st.error("Generate the server key first.")
        else:
            code, out, err = run_command(
                ["openssl", "req", "-new", "-key", str(APP_DIR / "server.key"), "-out", str(APP_DIR / "server.csr"), "-subj", subject],
                cwd=APP_DIR,
            )
            if code == 0:
                st.success("CSR created successfully.")
            else:
                st.error(err)

    if st.button("3. Self-sign certificate"):
        if not (APP_DIR / "server.csr").exists():
            st.error("Create the CSR first.")
        else:
            code, out, err = run_command(
                ["openssl", "x509", "-req", "-in", str(APP_DIR / "server.csr"), "-signkey", str(APP_DIR / "server.key"), "-out", str(APP_DIR / "server.crt"), "-days", "365"],
                cwd=APP_DIR,
            )
            if code == 0:
                st.success("Self-signed certificate generated.")
            else:
                st.error(err)

    if st.button("4. Inspect certificate"):
        cert_path = APP_DIR / "server.crt"
        if not cert_path.exists():
            st.error("Certificate not found.")
        else:
            code, out, err = run_command(
                ["openssl", "x509", "-in", str(cert_path), "-text", "-noout"],
                cwd=APP_DIR,
            )
            if code == 0:
                st.text_area("Certificate details", value=out, height=350)
            else:
                st.error(err)

    st.markdown(
        "**What the code does:** `req -new` creates a certificate signing request with the chosen subject fields. "
        "`x509 -req -signkey` produces a self-signed certificate valid for 365 days."
    )


# -----------------------------
# Experiment 5: Before vs After Traffic Simulation
# -----------------------------
with st.expander("Experiment 5: Plaintext vs Encrypted Traffic Simulation"):
    section_header(
        "Simulate what an attacker sees before and after encryption",
        "This is a simple app-level demonstration. It does not replace Wireshark, but it helps explain the same idea clearly for presentation purposes."
    )

    traffic_message = st.text_area(
        "API request example",
        value="username=jamal&password=MySecret123&token=QB999PAY&order=burger",
        key="traffic_message"
    )

    if st.button("Show before and after"):
        key = base64.urlsafe_b64encode(os.urandom(32))
        try:
            from cryptography.fernet import Fernet
            cipher = Fernet(key)
            encrypted = cipher.encrypt(traffic_message.encode())
            decrypted = cipher.decrypt(encrypted).decode()

            left, right = st.columns(2)
            with left:
                st.write("Without encryption")
                st.code(traffic_message, language="text")
            with right:
                st.write("With encryption")
                st.code(encrypted.decode(), language="text")

            st.write("Decrypted again for verification")
            st.code(decrypted, language="text")
        except ImportError:
            st.error("The 'cryptography' package is not installed. Install it with: pip install cryptography")

    st.markdown(
        "**What the code does:** It creates a random symmetric key, encrypts the message, and shows how the same API data looks unreadable after encryption. "
        "In your report, you can relate this to HTTPS and TLS protecting traffic in transit."
    )


# -----------------------------
# Report helper
# -----------------------------
with st.expander("Report Notes and ISO 27001/27002 Alignment"):
    st.markdown(
        "- **Experiment 1 (RSA):** Supports confidentiality and secure key exchange.\n"
        "- **Experiment 2 (AES):** Supports protection of data at rest.\n"
        "- **Experiment 3 (Hashing):** Supports secure authentication and password storage.\n"
        "- **Experiment 4 (PKI):** Supports server identity verification and certificate management.\n"
        "- **Experiment 5 (Traffic protection):** Supports protection of data in transit and resistance to interception.\n\n"
        "You can map these to ISO/IEC 27001 and 27002 controls on cryptography, access control, monitoring, secure communication, and information protection."
    )

    if st.button("Generate experiment timestamp note"):
        st.write(f"Evidence recorded on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
