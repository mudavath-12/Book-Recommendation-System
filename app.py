from flask import Flask, render_template, request
import requests

app = Flask(__name__)

GOOGLE_BOOKS_API_KEY = ""  # Optional, can be left blank

@app.route("/", methods=["GET", "POST"])
def index():
    books = []
    title = ""
    genre_filter = ""
    sort_by = ""

    if request.method == "POST":
        title = request.form.get("title")
        genre_filter = request.form.get("genre_filter", "")
        sort_by = request.form.get("sort_by", "")

        if title:
            # Fetch up to 50 books using pagination (maxResults=40 + 10)
            for start_index in [0, 40]:
                api_url = f"https://www.googleapis.com/books/v1/volumes?q={title}&startIndex={start_index}&maxResults=40"
                if GOOGLE_BOOKS_API_KEY:
                    api_url += f"&key={GOOGLE_BOOKS_API_KEY}"

                response = requests.get(api_url).json()
                for item in response.get("items", []):
                    volume = item.get("volumeInfo", {})
                    sale_info = item.get("saleInfo", {})
                    genre = ", ".join(volume.get("categories", ["General"]))
                    
                    # Apply genre filter if selected
                    if genre_filter and genre_filter.lower() not in genre.lower():
                        continue

                    price = "Not for Sale"
                    if "listPrice" in sale_info:
                        currency = sale_info.get("listPrice", {}).get("currencyCode", "")
                        amount = sale_info.get("listPrice", {}).get("amount", "Not for Sale")
                        price = f"{currency} {amount}"

                    books.append({
                        "title": volume.get("title", "N/A"),
                        "author": ", ".join(volume.get("authors", ["Unknown"])),
                        "genre": genre,
                        "thumbnail": volume.get("imageLinks", {}).get("thumbnail", ""),
                        "preview_link": volume.get("previewLink", "#"),
                        "rating": volume.get("averageRating", 0),  # Default 0 for sorting
                        "price": price,
                        "raw_price": sale_info.get("listPrice", {}).get("amount", float('inf')) if "listPrice" in sale_info else float('inf')
                    })

            # Apply sorting
            if sort_by == "rating":
                books.sort(key=lambda x: x["rating"], reverse=True)
            elif sort_by == "price":
                books.sort(key=lambda x: x["raw_price"])

    return render_template("index.html", books=books[:50], title=title)

if __name__ == "__main__":
    app.run(debug=True)
