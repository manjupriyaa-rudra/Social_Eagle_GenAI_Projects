from flask import Flask, jsonify, request
import random
from datetime import date

app = Flask(__name__)

power_quotes = [
    "keep leading with discipline and consistency.",
    "you are already on track. Push your limits today.",
    "every day of learning makes you stronger.",
    "your focus today builds your success tomorrow.",
    "stay consistent. Results will follow."
]

push_quotes = [
    "don’t wait for motivation. Start with action.",
    "even small steps matter. Keep learning.",
    "progress begins when you decide not to quit.",
    "your effort today changes your future.",
    "start now. Improvement comes later."
]

energizer_quotes = [
    "fear means growth. Take the first step.",
    "you are capable of more than you think.",
    "courage begins when excuses end.",
    "start today. Confidence comes later.",
    "learning begins the moment you try."
]

def get_daily_quote(quotes_list):
    today = date.today().toordinal()
    random.seed(today)
    return random.choice(quotes_list)

@app.route("/")
def home():
    return "Welcome Social Eagle Batch 5 - Personalized Quote Generator"

@app.route("/quote")
def quote():
    name = request.args.get("name", "Student")
    category = request.args.get("type", "power")

    if category == "power":
        message = get_daily_quote(power_quotes)
        title = "Power Quote"
    elif category == "push":
        message = get_daily_quote(push_quotes)
        title = "Push Quote"
    elif category == "energizer":
        message = get_daily_quote(energizer_quotes)
        title = "Super Energizer Quote"
    else:
        return jsonify({"error": "Invalid type. Use power, push or energizer"})

    final_quote = f"{name}, {message}"

    return jsonify({
        "team": "Social Eagle Batch 5",
        "category": title,
        "quote": final_quote
    })

if __name__ == "__main__":
    app.run(debug=True)
