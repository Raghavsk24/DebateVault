from flask import Flask, jsonify, request, render_template
import pandas as pd

app = Flask(__name__)

CSV_FILE_PATH = r'C:\Users\senth\Debate GPT\Cards\Valid_Card.csv'

@app.route('/api/cards', methods=['GET'])
def get_cards():
    try:
        # Load the CSV file
        df = pd.read_csv(CSV_FILE_PATH)

        # Get query and pagination parameters
        query = request.args.get('query', '').lower()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))

        # Filter dataset based on query
        if query:
            df = df[df['Tagline'].str.contains(query, case=False, na=False) |
                    df['Citation'].str.contains(query, case=False, na=False) |
                    df['Evidence'].str.contains(query, case=False, na=False)]

        # Paginate results
        total_cards = len(df)
        start = (page - 1) * limit
        end = start + limit
        paginated_df = df.iloc[start:end]

        # Convert to JSON
        cards = paginated_df.to_dict(orient='records')
        return jsonify({
            "cards": cards,
            "total": total_cards,
            "page": page,
            "limit": limit
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
