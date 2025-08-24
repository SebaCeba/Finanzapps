from app import create_app

app = create_app()

if __name__ == "__main__":
    print("📁 static_folder:", app.static_folder)
    print("🔗 static_url_path:", app.static_url_path)
    app.run(debug=True)