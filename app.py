import streamlit as st
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography import x509
from cryptography.x509.oid import NameOID
from Crypto.Cipher import AES, PKCS1_OAEP
import hashlib
import os
import datetime
import base64
st.set_page_config(
    page_title="FD Data Protection Lab",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
st.markdown("""
<style>

/* ===== APP BACKGROUND ===== */
[data-testid="stAppViewContainer"] {
    background-color: #191f22;
}

/* ===== MAIN CONTAINER ===== */
[data-testid="stMainBlockContainer"] {
    max-width: 1100px;
    padding-top: 1.5rem;
}

/* ===== FONT ===== */
html, body, [class*="css"] {
    font-family: "Segoe UI", Arial, sans-serif;
}

/* ===== TEXT ===== */
h1, h2, h3 {
    color: #f9fafb;
}

p, span, label {
    color: #e5e7eb;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background-color: #191f22;
    border-right: 1px solid #2f3a40;   /* 🔥 vertical divider */
}

[data-testid="stSidebar"] * {
    color: #f9fafb;
}

/* ===== MAIN AREA SEPARATOR (extra clarity) ===== */
[data-testid="stMain"] {
    border-left: 1px solid #2f3a40;    /* 🔥 ensures clear separation */
}

/* ===== BUTTONS ===== */
.stButton > button,
.stDownloadButton > button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    font-weight: 600;
    border: none;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background-color: #1d4ed8;
}

/* ===== FILE UPLOADER ===== */
[data-testid="stFileUploader"] {
    background-color: #2a3136;
    border-radius: 10px;
    padding: 0.8rem;
    border: 1px solid #3f4a50;
}

/* ===== FIX STREAMLIT HEADER (DO NOT HIDE) ===== */
[data-testid="stHeader"] {
    background: transparent;   /* keep burger menu visible */
}

/* ===== BURGER ICON VISIBILITY ===== */
[data-testid="collapsedControl"] {
    color: #ffffff !important;
}

/* ===== REMOVE EXTRA SPACE ===== */
.block-container {
    padding-top: 1rem;
}

/* ===== HORIZONTAL LINE FIX ===== */
hr {
    border: none;
    border-top: 1px solid #3f4a50;
}

</style>
""", unsafe_allow_html=True)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



menu = st.sidebar.radio(
    "FD Data Protection Lab",
    [
        "Home",
        "AES Data Protection",
        "RSA Key Management",
        "RSA Token Encryption",
        "Password Hashing",
        "TLS Certificate",
        "ISO Security Mapping",
        "Research Experiments"
    ]
)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if menu == "Home":
    st.markdown("""
<h1 style="font-size:36px; line-height:1.2; margin-bottom:8px;">
CSYM020 Internet Security – Data Protection Lab
</h1>
""", unsafe_allow_html=True)
    st.caption("FD Data Protection Lab")
    st.subheader("Secure Online Food Delivery Application Prototype")

    st.write("""
    This application demonstrates practical security controls for protecting sensitive data 
    in an online food delivery system.
    """)

    st.markdown("""
    ### Implemented Security Modules

    1. **AES Data Protection** - encrypt and decrypt customer/order files  
    2. **RSA Key Management** - generate public and private keys  
    3. **RSA Token Encryption** - protect payment/API tokens  
    4. **Password Hashing** - demonstrate SHA-256, SHA-512, salting, and avalanche effect  
    5. **TLS Certificate** - generate certificate files for server identity  
    6. **ISO Security Mapping** - map practical features to ISO 27001/27002 controls  
    """)

    st.info("Use the sidebar to select a security module.")



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#This experiment shows that customer and order data can be encrypted before storage. 
#If an attacker steals the file, the data is unreadable without the key.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from cryptography.fernet import Fernet
import streamlit as st

if menu == "AES Data Protection":
    st.header("AES Data Protection")

    # -------------------- ENCRYPTION --------------------
    uploaded_file = st.file_uploader(
        "Upload customer/order file",
        type=["txt", "csv"],
        key="upload_plain_file"
    )

    if uploaded_file:
        file_data = uploaded_file.read()

        st.subheader("Original File Content")
        st.code(file_data.decode(errors="ignore"))

        if st.button("Encrypt File"):
            key = Fernet.generate_key()
            cipher = Fernet(key)
            encrypted_data = cipher.encrypt(file_data)

            # store safely
            st.session_state["generated_aes_key"] = key
            st.session_state["encrypted_data"] = encrypted_data

            st.success("File encrypted successfully.")

    # -------------------- DOWNLOADS --------------------
    if "generated_aes_key" in st.session_state:
        st.download_button(
            "Download AES Key",
            data=st.session_state["generated_aes_key"],
            file_name="FD_aes_key.key",
            mime="application/octet-stream"
        )

    if "encrypted_data" in st.session_state:
        st.subheader("Encrypted Output")
        st.code(st.session_state["encrypted_data"].decode())

        st.download_button(
            "Download Encrypted File",
            data=st.session_state["encrypted_data"],
            file_name="FD_encrypted_order_data.bin",
            mime="application/octet-stream"
        )

    # -------------------- DECRYPTION --------------------
    st.divider()
    st.subheader("Decrypt File")

    encrypted_file = st.file_uploader(
        "Upload encrypted file",
        type=["bin"],
        key="uploaded_encrypted_file"
    )

    aes_key_file = st.file_uploader(
        "Upload AES key",
        type=["key"],
        key="uploaded_aes_key"
    )

    if encrypted_file and aes_key_file:
        encrypted_content = encrypted_file.read()
        aes_key = aes_key_file.read()

        try:
            cipher = Fernet(aes_key)
            decrypted_data = cipher.decrypt(encrypted_content)

            st.success("File decrypted successfully.")
            st.code(decrypted_data.decode(errors="ignore"))

            st.download_button(
                "Download Decrypted File",
                data=decrypted_data,
                file_name="FD_decrypted_data.txt",
                mime="text/plain"
            )

        except Exception:
            st.error("Decryption failed. Make sure the AES key matches the encrypted file.")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#RSA Key Management
#Purpose

#This section proves how FD can generate public/private keys for secure token exchange.

if menu == "RSA Key Management":
    st.header("Experiment 2: RSA Key Management")

    if st.button("Generate RSA-2048 Key Pair"):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        public_key = private_key.public_key()

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        st.session_state["rsa_private_pem"] = private_pem
        st.session_state["rsa_public_pem"] = public_pem

        st.success("RSA key pair generated successfully.")

    if (
        "rsa_public_pem" in st.session_state
        and st.session_state["rsa_public_pem"] is not None
        and "rsa_private_pem" in st.session_state
        and st.session_state["rsa_private_pem"] is not None
    ):
        st.subheader("Public Key")
        st.code(st.session_state["rsa_public_pem"].decode())

        st.download_button(
            "Download Public Key",
            data=st.session_state["rsa_public_pem"],
            file_name="FD_public_key.pem",
            mime="application/x-pem-file"
        )

        st.subheader("Private Key")
        st.code(st.session_state["rsa_private_pem"].decode())

        st.download_button(
            "Download Private Key",
            data=st.session_state["rsa_private_pem"],
            file_name="FD_private_key.pem",
            mime="application/x-pem-file"
        )
    else:
        st.info("Click 'Generate RSA-2048 Key Pair' to create downloadable keys.")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#Experiment 4: Token Encryption and Decryption
#Purpose

#This simulates encrypting a payment token or API token.

if menu == "RSA Token Encryption":
    st.header("Experiment 3: RSA Token Encryption")

    token = st.text_input(
        "Enter fake API/payment token",
        value="QB-PAYMENT-TOKEN-2026-999"
    )

    public_key_file = st.file_uploader("Upload RSA Public Key", type=["pem"], key="pubkey")

    if public_key_file and st.button("Encrypt Token"):
        public_key = serialization.load_pem_public_key(public_key_file.read())

        encrypted_token = public_key.encrypt(
            token.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        st.subheader("Encrypted Token")
        st.code(encrypted_token.hex())

        st.download_button(
            "Download Encrypted Token",
            encrypted_token,
            file_name="encrypted_token.bin"
        )

    st.divider()
    st.subheader("Decrypt Token")

    encrypted_token_file = st.file_uploader("Upload Encrypted Token", type=["bin"], key="encrypted_token")
    private_key_file = st.file_uploader("Upload RSA Private Key", type=["pem"], key="privatekey")

    if encrypted_token_file and private_key_file and st.button("Decrypt Token"):
        private_key = serialization.load_pem_private_key(
            private_key_file.read(),
            password=None
        )

        decrypted_token = private_key.decrypt(
            encrypted_token_file.read(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        st.success("Token decrypted successfully.")
        st.code(decrypted_token.decode())

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Password Hashing
#Purpose

#This shows password protection, salting, and avalanche effect.

if menu == "Password Hashing":
    st.header("Experiment 4: Password Hashing")

    password = st.text_input("Enter password", value="FDLogin2026")
    changed_password = st.text_input("Enter slightly changed password", value="FDLogin2027")

    if st.button("Generate Hashes"):
        salt = os.urandom(16)

        sha256_hash = hashlib.sha256(password.encode()).hexdigest()
        sha512_hash = hashlib.sha512(password.encode()).hexdigest()
        changed_hash = hashlib.sha256(changed_password.encode()).hexdigest()
        salted_hash = hashlib.sha256(salt + password.encode()).hexdigest()

        st.subheader("SHA-256")
        st.code(sha256_hash)

        st.subheader("SHA-512")
        st.code(sha512_hash)

        st.subheader("Avalanche Effect")
        st.write("One small change creates a completely different SHA-256 hash.")
        st.code(changed_hash)

        st.subheader("Salt")
        st.code(salt.hex())

        st.subheader("Salted SHA-256")
        st.code(salted_hash)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#TLS Certificate Generator
#Purpose

#This creates server identity files for www.FDDataProtectionLab.co.uk.

if menu == "TLS Certificate":
    st.header("Experiment 5: TLS Certificate Generator")

    common_name = st.text_input("Common Name", value="www.fddataprotectionlab.co.uk")
    organisation = st.text_input("Organisation", value="FD Data Protection Lab Ltd")
    country = st.text_input("Country", value="GB")

    if st.button("Generate TLS Certificate"):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, country),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organisation),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])

        certificate = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .sign(private_key, hashes.SHA256())
        )

        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        cert_pem = certificate.public_bytes(serialization.Encoding.PEM)

        st.session_state["tls_private_key_pem"] = private_key_pem
        st.session_state["tls_cert_pem"] = cert_pem

        st.success("TLS certificate generated successfully.")

    if (
        "tls_private_key_pem" in st.session_state
        and st.session_state["tls_private_key_pem"] is not None
        and "tls_cert_pem" in st.session_state
        and st.session_state["tls_cert_pem"] is not None
    ):
        st.subheader("TLS Certificate")
        st.code(st.session_state["tls_cert_pem"].decode())

        st.download_button(
            "Download Server Private Key",
            data=st.session_state["tls_private_key_pem"],
            file_name="FD_server_private_key.pem",
            mime="application/x-pem-file"
        )

        st.download_button(
            "Download TLS Certificate",
            data=st.session_state["tls_cert_pem"],
            file_name="FD_tls_certificate.crt",
            mime="application/x-x509-ca-cert"
        )
    else:
        st.info("Click 'Generate TLS Certificate' to create downloadable certificate files.")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



#ISO 27001/27002 Mapping Section


if menu == "ISO Security Mapping":
    st.header("ISO 27001/27002 Control Mapping")

    st.table({
        "App Feature": [
            "AES file encryption",
            "RSA key generation",
            "Password hashing",
            "TLS certificate generation",
            "Downloadable encrypted files",
            "Key separation"
        ],
        "Security Purpose": [
            "Protects data at rest",
            "Supports secure key exchange",
            "Protects user credentials",
            "Supports server identity verification",
            "Creates practical evidence of encryption",
            "Separates public and private cryptographic material"
        ],
        "ISO 27001/27002 Link": [
            "Cryptography and information protection",
            "Cryptographic key management",
            "Access control and authentication",
            "Secure communication",
            "Information handling",
            "Key management and access restriction"
        ]
    })



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ==============================
# Research Experiments Section
# ==============================

if menu == "Research Experiments":

    st.title("🔬 Research Experiments (CSYM020)")
    st.write("This section demonstrates practical cryptographic experiments supporting the research paper.")

    experiment = st.selectbox(
        "Select Experiment",
        [
            "AES File Encryption",
            "RSA Token Encryption",
            "Password Hashing",
            "TLS Certificate Generation",
            "Secure Messaging (E2EE Simulation)"
        ]
    )

    # ==============================
    # 1. AES FILE ENCRYPTION
    # ==============================
    if experiment == "AES File Encryption":

        st.subheader("Experiment 1: AES-256 File Encryption")
        uploaded_file = st.file_uploader("Upload file", type=["txt", "csv"])

        if uploaded_file:
            data = uploaded_file.read()

            key = get_random_bytes(32)
            cipher = AES.new(key, AES.MODE_GCM)

            ciphertext, tag = cipher.encrypt_and_digest(data)

            st.success("File Encrypted Successfully")

            st.download_button("Download Encrypted File", ciphertext)
            st.download_button("Download Key", key)

    # ==============================
    # 2. RSA TOKEN ENCRYPTION
    # ==============================
    elif experiment == "RSA Token Encryption":

        st.subheader("Experiment 2: RSA Token Encryption")

        token = st.text_input("Enter fake API/payment token")

        if st.button("Generate RSA Keys"):
            key = RSA.generate(2048)
            private_key = key.export_key()
            public_key = key.publickey().export_key()

            st.session_state.public_key = public_key
            st.session_state.private_key = private_key

            st.success("Keys Generated")

            st.download_button("Download Public Key", public_key)
            st.download_button("Download Private Key", private_key)

        if token and "public_key" in st.session_state:
            rsa_key = RSA.import_key(st.session_state.public_key)
            cipher = PKCS1_OAEP.new(rsa_key)

            encrypted_token = cipher.encrypt(token.encode())

            st.write("Encrypted Token:")
            st.code(base64.b64encode(encrypted_token).decode())

    # ==============================
    # 3. PASSWORD HASHING
    # ==============================
    elif experiment == "Password Hashing":

        st.subheader("Experiment 3: Password Hashing (SHA-256 + Salt)")

        password = st.text_input("Enter Password", type="password")

        if password:
            salt = os.urandom(16)
            hashed = hashlib.sha256(salt + password.encode()).hexdigest()

            st.write("Salt:", salt.hex())
            st.write("Hashed Password:", hashed)

    # ==============================
    # 4. TLS CERTIFICATE GENERATION
    # ==============================
    elif experiment == "TLS Certificate Generation":

        st.subheader("Experiment 4: TLS Certificate Simulation")

        st.write("Use OpenSSL command below in terminal:")

        st.code("""
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
        """)

        st.info("This demonstrates secure HTTPS communication setup.")

    # ==============================
    # 5. SECURE MESSAGING (E2EE)
    # ==============================
  elif experiment == "Secure Messaging (E2EE Simulation)":

    st.subheader("Experiment 5: Secure Messaging Simulation")

    message = st.text_area("Enter Message")

    if st.button("Encrypt Message"):
        key = get_random_bytes(32)
        cipher = AES.new(key, AES.MODE_GCM)

        ciphertext, tag = cipher.encrypt_and_digest(message.encode())

        st.session_state.msg_key = key
        st.session_state.msg_nonce = cipher.nonce
        st.session_state.msg_tag = tag
        st.session_state.msg_cipher = ciphertext

        st.write("Encrypted Message:")
        st.code(base64.b64encode(ciphertext).decode())

    if st.button("Decrypt Message"):
        if all(k in st.session_state for k in ["msg_key", "msg_nonce", "msg_tag", "msg_cipher"]):
            try:
                cipher = AES.new(
                    st.session_state.msg_key,
                    AES.MODE_GCM,
                    nonce=st.session_state.msg_nonce
                )

                decrypted = cipher.decrypt_and_verify(
                    st.session_state.msg_cipher,
                    st.session_state.msg_tag
                )

                st.success("Decrypted Message:")
                st.write(decrypted.decode("utf-8"))

            except Exception:
                st.error("Decryption failed. Encrypt the message again first.")
        else:
            st.warning("Please encrypt a message first.")

#---------------------------------------------------------------------------------------------------------


st.markdown("""
---
**FD Data Protection Lab**  
Mian Jamal Shah | CSYM020 Internet Security | University of Northampton | copyrights - 2026
""")