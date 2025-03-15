import csv
import os
import random
import caption  # imports the create function from caption.py


def random_text():
    # Generate a random text string (3-6 random words from a fixed list)
    words = [
        "lorem",
        "ipsum",
        "dolor",
        "sit",
        "amet",
        "consectetur",
        "adipiscing",
        "elit",
    ]
    return " ".join(random.choices(words, k=random.randint(3, 6)))


def load_templates(csv_path):
    templates = []
    with open(csv_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Expecting CSV columns "ID" and "box_count"
            templates.append(
                {"template_id": row["ID"], "box_count": int(row["box_count"])}
            )
    return templates


def main():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "dataset", "data.csv")
    templates = load_templates(csv_path)
    if not templates:
        print("No templates found in data.csv")
        return

    for i in range(10):
        template = random.choice(templates)
        boxes = [random_text() for _ in range(template["box_count"])]
        try:
            label = caption.create(
                {"template_id": template["template_id"], "boxes": boxes}
            )
            print(f"Meme {i + 1} generated with label: {label}")
        except Exception as ex:
            print(f"Error generating meme {i + 1}: {ex}")


if __name__ == "__main__":
    main()
