
import requests
import random
import streamlit as st

# =============================
# CONFIG
# =============================
API_BASE = "https://movie-rec-466x.onrender.com" or "http://127.0.0.1:8000"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(
    page_title="Movie Discovery Engine",
    page_icon="🎬",
    layout="wide"
)

# =============================
# GLOBAL STYLE
# =============================
st.markdown("""
<style>

html, body, [class*="css"]{
background:#0a0a0f;
color:white;
font-family: 'Inter', sans-serif;
}

.block-container{
max-width:1400px;
padding-top:1rem;
}

/* Hero */
.hero{
padding:30px;
border-radius:18px;
background:linear-gradient(90deg,#1e1e2f,#151522);
border:1px solid rgba(255,255,255,0.08);
}

/* Gradient title */
.title{
font-size:46px;
font-weight:700;
background:linear-gradient(90deg,#ff4b2b,#ff416c);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
}

/* subtitle */
.subtitle{
color:#9ca3af;
margin-top:-10px;
}

/* glass panel */
.glass{
background:rgba(255,255,255,0.05);
border-radius:18px;
padding:20px;
border:1px solid rgba(255,255,255,0.08);
}

/* movie card */
.movie-card{
border-radius:14px;
overflow:hidden;
transition:all .25s ease;
}

.movie-card:hover{
transform:scale(1.06);
box-shadow:0 8px 40px rgba(255,80,80,0.5);
}

/* movie title */
.movie-title{
text-align:center;
font-size:0.9rem;
margin-top:6px;
height:2.2rem;
overflow:hidden;
}

/* rating badge */
.rating{
background:#ff416c;
padding:2px 6px;
border-radius:6px;
font-size:0.75rem;
position:absolute;
margin:6px;
}

.small{
color:#9ca3af;
font-size:0.9rem;
}

</style>
""", unsafe_allow_html=True)

# =============================
# STATE
# =============================
if "view" not in st.session_state:
    st.session_state.view = "home"

if "movie_id" not in st.session_state:
    st.session_state.movie_id = None


def goto_home():
    st.session_state.view = "home"
    st.session_state.movie_id = None
    st.rerun()


def goto_details(mid):
    st.session_state.view = "details"
    st.session_state.movie_id = mid
    st.rerun()


# =============================
# API
# =============================
@st.cache_data(ttl=30)
def api(path, params=None):
    try:
        r = requests.get(API_BASE + path, params=params, timeout=25)
        if r.status_code >= 400:
            return None
        return r.json()
    except:
        return None


# =============================
# MOVIE GRID
# =============================
def movie_grid(cards, cols=6):

    if not cards:
        st.info("No movies")
        return

    rows = (len(cards)+cols-1)//cols
    idx = 0

    for r in range(rows):

        columns = st.columns(cols)

        for c in range(cols):

            if idx >= len(cards):
                break

            m = cards[idx]
            idx += 1

            with columns[c]:

                st.markdown('<div class="movie-card">', unsafe_allow_html=True)

                poster = m.get("poster_url")
                title = m.get("title")
                mid = m.get("tmdb_id")

                if poster:
                    st.image(poster)

                if st.button("Open", key=f"{mid}_{idx}"):

                    goto_details(mid)

                st.markdown(
                    f'<div class="movie-title">{title}</div>',
                    unsafe_allow_html=True
                )

                st.markdown('</div>', unsafe_allow_html=True)


# =============================
# SIDEBAR
# =============================
with st.sidebar:

    st.markdown("## 🎬 Explorer")

    if st.button("🏠 Home"):
        goto_home()

    st.divider()

    st.markdown("### Browse")

    category = st.selectbox(
        "Category",
        ["trending","popular","top_rated","upcoming","now_playing"]
    )

    cols = st.slider("Grid Columns",4,8,6)

    st.divider()

    if st.button("🎲 Surprise Me"):

        data = api("/home",{"category":"popular","limit":30})

        if data:
            movie = random.choice(data)
            goto_details(movie["tmdb_id"])


# =============================
# HERO SECTION
# =============================
st.markdown(
"""
<div class="hero">
<div class="title">🎬 Movie Discovery Engine</div>
<div class="subtitle">
AI powered movie recommendations • discover trending cinema • explore new films
</div>
</div>
""",
unsafe_allow_html=True
)

st.divider()

# =============================
# HOME VIEW
# =============================
if st.session_state.view == "home":

    query = st.text_input(
        "Search movies",
        placeholder="Try: Batman, Avengers, Interstellar..."
    )

    st.divider()

    # SEARCH
    if query:

        with st.spinner("Searching..."):

            data = api("/tmdb/search",{"query":query})

        if data and "results" in data:

            cards=[]

            for m in data["results"][:24]:

                cards.append({
                    "tmdb_id":m["id"],
                    "title":m.get("title"),
                    "poster_url":f"{TMDB_IMG}{m['poster_path']}" if m.get("poster_path") else None
                })

            st.markdown("### 🔎 Search Results")

            movie_grid(cards,cols)

        else:
            st.warning("No results")

    # HOME SECTIONS
    else:

        tab1,tab2,tab3 = st.tabs(["🔥 Trending","⭐ Top Rated","🎬 Now Playing"])

        with tab1:

            data = api("/home",{"category":"trending","limit":24})

            if data:
                movie_grid(data,cols)

        with tab2:

            data = api("/home",{"category":"top_rated","limit":24})

            if data:
                movie_grid(data,cols)

        with tab3:

            data = api("/home",{"category":"now_playing","limit":24})

            if data:
                movie_grid(data,cols)

# =============================
# DETAILS VIEW
# =============================
elif st.session_state.view == "details":

    mid = st.session_state.movie_id

    if st.button("← Back"):
        goto_home()

    data = api(f"/movie/id/{mid}")

    if not data:
        st.error("Movie not found")
        st.stop()

    left,right = st.columns([1,2])

    with left:

        st.markdown('<div class="glass">',unsafe_allow_html=True)

        if data.get("poster_url"):
            st.image(data["poster_url"])

        st.markdown('</div>',unsafe_allow_html=True)

    with right:

        st.markdown('<div class="glass">',unsafe_allow_html=True)

        st.markdown(f"## {data.get('title')}")

        st.markdown(
        f"<div class='small'>Release: {data.get('release_date')}</div>",
        unsafe_allow_html=True)

        genres=", ".join([g["name"] for g in data.get("genres",[])])

        st.markdown(
        f"<div class='small'>Genres: {genres}</div>",
        unsafe_allow_html=True)

        st.markdown("---")

        st.write(data.get("overview"))

        st.markdown('</div>',unsafe_allow_html=True)

    if data.get("backdrop_url"):
        st.image(data["backdrop_url"],use_column_width=True)

    st.divider()

    st.markdown("### 🎯 Recommendations")

    bundle = api("/movie/search",{
        "query":data.get("title"),
        "tfidf_top_n":12,
        "genre_limit":12
    })

    if bundle:

        tfidf_cards=[]

        for x in bundle.get("tfidf_recommendations",[]):

            tmdb=x.get("tmdb")

            if tmdb:

                tfidf_cards.append({
                    "tmdb_id":tmdb["tmdb_id"],
                    "title":tmdb["title"],
                    "poster_url":tmdb["poster_url"]
                })

        st.markdown("#### Similar Movies")

        movie_grid(tfidf_cards,cols)

        st.markdown("#### More Like This")

        movie_grid(bundle.get("genre_recommendations"),cols)

    else:
        st.info("No recommendations available")

