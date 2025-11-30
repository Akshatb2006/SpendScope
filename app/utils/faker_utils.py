from faker import Faker
import random

fake = Faker()

def generate_transaction_description() -> str:
    templates = [
        f"{fake.company()} - Purchase",
        f"{fake.word().capitalize()} Store",
        f"Payment to {fake.name()}",
        f"{fake.city()} - {fake.word()}"
    ]
    return random.choice(templates)

def generate_merchant_name() -> str:
    return fake.company()