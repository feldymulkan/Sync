import subprocess
import os

def generate_ssl_certificate(cert_name="server2", passphrase="server2"):
    cert_file = f"{cert_name}-cert.pem"
    key_file = f"{cert_name}-key.pem"

    # Periksa apakah sertifikat sudah ada
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        # Gunakan OpenSSL untuk membuat sertifikat SSL self-signed tanpa batasan waktu kadaluarsa
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:4096", "-keyout", key_file,
            "-out", cert_file, "-subj", f"/CN={cert_name}", "-passout", f"pass:{passphrase}"
        ])

        print(f"Sertifikat SSL '{cert_file}' dan kunci pribadi '{key_file}' telah berhasil dibuat.")

    return cert_file, key_file

# Panggil fungsi untuk membuat sertifikat SSL dan kunci pribadi di direktori saat ini
generate_ssl_certificate()
