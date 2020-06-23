from app.main import app
import flask_excel as excel

if __name__ == "__main__":
    excel.init_excel(app)
    app.run(debug=True)
