from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests

app = Flask(__name__, static_folder='static')
CORS(app)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    try:
        book_title = request.args.get('title', '')
        if book_title :
            return jsonify({
                'recommendations': [],
                'total_found': 0,
                'message': 'No books found'
            }), 404
        if not book_title:
            return jsonify({
                'recommendations': [],
                'total_found': 0,
                'message': 'Book title is required'
            }), 400

        url = f"https://openlibrary.org/search.json?q={book_title}&limit=10"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        if not data.get('docs'):
            return jsonify({
                'recommendations': [],
                'total_found': 0,
                'message': 'No books found'
            }), 404

        recommendations = []
        seen_titles = set()

        for book in data['docs']:
            if len(recommendations) >= 5:
                break
                
            title = book.get('title', 'Unknown Title')
            if title in seen_titles:
                continue
            seen_titles.add(title)

            # Get book description
            description = 'No description available'
            if book.get('key'):
                try:
                    work_url = f"https://openlibrary.org{book['key']}.json"
                    work_response = requests.get(work_url)
                    if work_response.ok:
                        work_data = work_response.json()
                        description = work_data.get('description', '')
                        if isinstance(description, dict):
                            description = description.get('value', 'No description available')
                except:
                    pass

            book_info = {
                'title': title,
                'authors': book.get('author_name', ['Unknown Author']),
                'description': description,
                'publish_year': book.get('first_publish_year', 'Unknown'),
                'language': 'English',
                'subjects': book.get('subject', [])[:3] if book.get('subject') else []
            }
            
            cover_id = book.get('cover_i')
            if cover_id:
                book_info['image_url'] = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
            else:
                book_info['image_url'] = "https://via.placeholder.com/200x300?text=No+Image"
            
            recommendations.append(book_info)

        return jsonify({
            'recommendations': recommendations,
            'total_found': len(recommendations),
            'message': None
        })

    except requests.RequestException as e:
        return jsonify({
            'recommendations': [],
            'total_found': 0,
            'message': f'API error: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'recommendations': [],
            'total_found': 0,
            'message': f'Server error: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
    
    
    