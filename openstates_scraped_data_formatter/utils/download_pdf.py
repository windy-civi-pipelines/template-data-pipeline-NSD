from urllib import request


def download_bill_pdf(content, save_path, bill_identifier):
    versions = content.get("versions", [])
    if not versions:
        print("⚠️ No versions found for bill")
        return

    files_dir = save_path / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    for version in versions:
        for link in version.get("links", []):
            url = link.get("url")
            if url and url.endswith(".pdf"):
                try:
                    response = request.get(url, timeout=10)
                    if response.status_code == 200:
                        filename = f"{bill_identifier}.pdf"
                        file_path = files_dir / filename
                        with open(file_path, "wb") as f:
                            f.write(response.content)
                        print(f"📄 Downloaded PDF: {filename}")
                    else:
                        print(
                            f"⚠️ Failed to download PDF: {url} (status {response.status_code})"
                        )
                except Exception as e:
                    print(f"❌ Error downloading PDF: {url} ({e})")
