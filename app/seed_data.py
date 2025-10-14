import random
from faker import Faker
from app.utils.db import get_db_connection

fake = Faker()

def seed_data():
    conn = get_db_connection()
    cur = conn.cursor()

    # 🧑‍🤝‍🧑 Insert users
    print("🧑‍🤝‍🧑 Inserting users...")
    for i in range(10):
        username = f"user{i+1}"
        email = f"user{i+1}@example.com"
        password = "hashedpassword123"
        cur.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;",
            (username, email, password)
        )

    # 🔄 Fetch all real user IDs from DB
    cur.execute("SELECT id FROM users;")
    user_ids = [row[0] for row in cur.fetchall()]

    # 📝 Insert posts
    print("📝 Inserting posts...")
    for i in range(100):
        user_id = random.choice(user_ids)
        content = fake.sentence(nb_words=12)
        cur.execute(
            "INSERT INTO posts (user_id, content) VALUES (%s, %s);",
            (user_id, content)
        )

    # 🎉 Insert events
    print("🎉 Inserting events...")
    for i in range(50):
        user_id = random.choice(user_ids)
        title = fake.catch_phrase()
        description = fake.text(max_nb_chars=120)
        event_date = fake.date_time_between(start_date="-10d", end_date="+30d")
        location = fake.city()
        cur.execute(
            "INSERT INTO events (user_id, title, description, event_date, location) VALUES (%s, %s, %s, %s, %s);",
            (user_id, title, description, event_date, location)
        )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Dummy data inserted successfully!")


if __name__ == "__main__":
    seed_data()
