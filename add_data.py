from app import app
from models import db, Painting

with app.app_context():
    p1 = Painting(
        title_en="The Edge of Good and Evil",
        title_vi="Ngưỡng Thiện Ác",
        description_en="Material: Woodblock print",
        description_vi="Chất liệu: tranh in mộc bản",
        image="painting1.jpg"
    )

    db.session.add(p1)
    db.session.commit()

    print("Added p1 successfully!")