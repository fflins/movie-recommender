from flask import Flask, render_template, request
import pickle
import requests

app = Flask(__name__)

# Função para buscar o pôster do filme
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={yourAPIkeyhere}&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return None

def recommend(movie):
    # Verificar se o filme existe no dataframe
    if movie not in movies['title'].values:
        return [], []
    
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        poster_url = fetch_poster(movie_id)
        if poster_url:
            recommended_movie_posters.append(poster_url)
            recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters

# Carregar os dados
movies = pickle.load(open('artifacts/movie_list.pkl', 'rb'))
similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))

@app.route('/', methods=['GET', 'POST'])
def index():
    error_message = None
    recommended_movie_names = []
    recommended_movie_posters = []
    
    if request.method == 'POST':
        selected_movie = request.form['movie']
        
        # Verificar se o campo está vazio
        if not selected_movie:
            error_message = "Por favor, digite o nome de um filme."
        # Verificar se o filme existe no dataframe
        elif selected_movie not in movies['title'].values:
            error_message = f"O filme '{selected_movie}' não foi encontrado. Por favor, escolha um filme da lista."
        else:
            recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
            if not recommended_movie_names:
                error_message = f"Não foi possível encontrar recomendações para '{selected_movie}'."
                
    return render_template('index.html', 
                          movie_list=movies['title'].values,
                          recommended_movie_names=recommended_movie_names, 
                          recommended_movie_posters=recommended_movie_posters,
                          error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)