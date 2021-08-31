import pandas as pd
import numpy as np
from PIL import Image
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go


anime_df = pd.read_csv("demographic_anime.csv")
Types = anime_df.type.unique().tolist()
All_Types = dict(zip([Type for Type in Types],[pd.read_csv(f"{Type}_similarity.csv", index_col = "name") for Type in Types]))

def plot_trend(Type = None):
    """
    This function plots trends of anime formats 
    """
    df = anime_df.copy()
    df = df[df["type"]==Type]
    data = df[["name","members"]].sort_values(by = "members", ascending = False)[:10][::-1]
    fig = go.Figure([go.Bar(x=data["name"].values, y=data["members"].values,marker_color = "skyblue")])
    return fig
    #fig = px.bar(df[["name","members"]].sort_values(by = "members", ascending = False)[:10][::-1], x="name", y="members", color="members", title = f"Trending in {Type}") 
    #fig.show()

#filter
def filter_agg(x):
    return x.quantile(0.9)

anime_rating_filter = anime_df.groupby(by = "type").agg(filter_agg)["vote count"]

def Recommended_anime(Type = None):
    """
    returns top 10 anime in a specific type of anime (TV, OVA, Movie etc.)
    """
    df = anime_df.copy()
    df = df[df["type"]==Type].loc[df['vote count'] >= anime_rating_filter[Type]]
    N_max = df[df["type"]==Type]["vote count"].max()
    R0 = df[df["type"]==Type]["rating"].mean()
    R = df[df["type"]==Type]["rating"]
    n = df[df["type"]==Type]["vote count"]
    w = n/N_max
    df["Score"] = w*R + (1-w)*R0 #Bayesyan average
    df = df.sort_values('Score', ascending=False)[:10]
    return df[["name","Score"]].reset_index().drop("index",axis = 1)


def get_similar_anime(Type, anime_name, n_rec = 10):
    """
    Gives user recommendations based on the anime he likes.
    """
    try: 
        if anime_name not in All_Types[Type].index.tolist():
            return f"please write a proper name for example: {All_Types[Type].sample().index[0]}"
        else:
            sim_animes = All_Types[Type].sort_values(by=anime_name, ascending=False).index[1:n_rec+1].tolist()
            return pd.DataFrame({f"anime {Type}":sim_animes},index = list(range(1,n+1)))
    except:
        return f"check parameters:\n\tType = {Type},anime_name = {anime_name},n_rec = {n_rec}"
        
st.title("Anime Recommendation 🐱‍👓")
image = Image.open('anime.jpg')
st.image(image)
st.write('---')


html_temp = """
<div style ="background-color:skyblue;padding:13px">
<h1 style ="color:black;text-align:center;font-family:Comic Sans MS;">Got nothing new to watch? Get some anime recommendations!</h1>
</div>
"""
st.markdown(html_temp, unsafe_allow_html = True)
st.write('---')

Type = st.selectbox("What type of format do you want to watch?", options = Types)

if st.button(f"Popular {Type}"):
    st.write(f"Recommended in {Type}")
    st.write(Recommended_anime(Type))
st.write('---')    
if st.button(f"Trending on {Type}"):
    st.write(f"Trending on {Type} by member count")
    st.plotly_chart(plot_trend(Type))
    
st.write('---')  
st.selectbox("anime list: (copy from here if needed)",All_Types[Type].index.tolist())
anime_name = st.text_input("Enter anime name")
n = st.slider("number of recommendations",1,20,step = 1)

if st.button(f"{Type}: {anime_name}"):
    st.write("you might also like:")
    st.write(get_similar_anime(Type, anime_name, n))
    