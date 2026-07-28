from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models.user import User
from app.models.note import Note
from faker import Faker

fake = Faker()

app = create_app()

CATEGORIES = ["general", "work", "personal", "ideas"]


def seed():
    with app.app_context():
        print("Dropping existing tables...")
        db.drop_all()
        db.create_all()

        print("Seeding users...")
        users = []
        for _ in range(5):
            user = User(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
            )
            user.password = "password123"
            users.append(user)
            db.session.add(user)

        # Add a known test user for easy manual testing
        test_user = User(username="testuser", email="test@example.com")
        test_user.password = "password123"
        users.append(test_user)
        db.session.add(test_user)

        db.session.commit()
        print(f"  Created {len(users)} users.")

        print("Seeding notes...")
        note_count = 0
        for user in users:
            for _ in range(fake.random_int(min=3, max=8)):
                note = Note(
                    title=fake.sentence(nb_words=5).rstrip("."),
                    content=fake.paragraph(nb_sentences=3),
                    category=fake.random_element(CATEGORIES),
                    is_pinned=fake.boolean(chance_of_getting_true=20),
                    user_id=user.id,
                )
                db.session.add(note)
                note_count += 1

        db.session.commit()
        print(f"  Created {note_count} notes.")
        print("Seeding complete!")
        print("\nTest credentials: username=testuser | password=password123")


if __name__ == "__main__":
    seed()
